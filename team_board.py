"""Custom-drawn team panel: coloured banner, column headings and one card per player"""
import tkinter as tk
import tkinter.font as tkfont

RANK_COLORS = {
    'Iron': '#8b9097', 'Bronze': '#c08552', 'Silver': '#c9d2da', 'Gold': '#eab84b',
    'Platinum': '#3fc3cc', 'Diamond': '#c78ef7', 'Ascendant': '#3fd88f',
    'Immortal': '#ff5c7c', 'Radiant': '#fff0a6',
}
PARTY_COLORS = ('#17d4b0', '#f5a524', '#ff7ab6', '#4fb3ff', '#c3e66e', '#ff8a5c', '#e8d36a', '#9aa5b1')
PARTY_LABELS = {2: "DUO", 3: "TRIO", 4: "4-STACK", 5: "5-STACK"}

# (key, heading, width, anchor); the player column takes the remaining width
COLUMNS = (
    ('player', 'PLAYER', None, 'w'),
    ('rank', 'RANK', 118, 'w'),
    ('peak', 'PEAK', 118, 'w'),
    ('level', 'LVL', 44, 'center'),
    ('win', 'WIN %', 54, 'center'),
    ('kd', 'K/D', 62, 'center'),
    ('hs', 'HS %', 52, 'center'),
    ('info', 'INFO', 58, 'center'),
)
ROWS = 5
GUTTER = 20       # Room for the party strip left of the cards
BANNER_H = 36
HEADING_H = 24
ROW_GAP = 4
RIGHT_PAD = 4

DARK_TEXT = '#0b0f14'


def pick_family(*names):
    """First installed font family out of names (Bahnschrift ships with Windows 10+)"""
    installed = set(tkfont.families())
    return next((n for n in names if n in installed), 'Segoe UI')


def blend(color, other, amount):
    """Mix two #rrggbb colours; amount 0 = color, 1 = other"""
    a = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def rank_color(rank):
    return RANK_COLORS.get((rank or '').split(' ')[0])


class TeamBoard(tk.Canvas):
    """
    rows: dicts with player, name, tag, agent, kind ('you' / 'incognito' / 'normal'),
    rank, peak, level, level_muted, win, kd, hs (each (text, value or None)),
    info [(text, colour)], party (number, confirmed, size) or None.
    """

    def __init__(self, parent, colors, title, side_color, on_hover=None, on_leave=None, on_open=None):
        super().__init__(parent, bg=colors['panel'], highlightthickness=0, bd=0)
        self.colors = colors
        self.title = title.upper()
        self.side_color = side_color
        self.on_hover, self.on_leave, self.on_open = on_hover, on_leave, on_open

        condensed = pick_family('Bahnschrift SemiBold Condensed', 'Bahnschrift Condensed', 'Segoe UI Semibold')
        semibold = pick_family('Bahnschrift SemiBold', 'Segoe UI Semibold')
        regular = pick_family('Bahnschrift', 'Segoe UI')
        self.fonts = {
            'banner': tkfont.Font(family=condensed, size=15, slant='italic'),
            'chip': tkfont.Font(family=semibold, size=9),
            'heading': tkfont.Font(family=semibold, size=7),
            'name': tkfont.Font(family=condensed, size=14),
            'name_small': tkfont.Font(family=condensed, size=12),
            'tag': tkfont.Font(family=regular, size=9),
            'agent': tkfont.Font(family=semibold, size=7),
            'rank': tkfont.Font(family=condensed, size=12),
            'kd': tkfont.Font(family=condensed, size=19),
            'kd_small': tkfont.Font(family=condensed, size=16),
            'stat': tkfont.Font(family=semibold, size=11),
            'muted': tkfont.Font(family=regular, size=9),
            'party': tkfont.Font(family=semibold, size=7),
            'message': tkfont.Font(family=regular, size=10),
        }

        self._rows = []
        self._message = "Waiting for match data..."
        self._count = 0
        self._state = None     # 'yours', 'enemy' or None
        self._hover = None
        self._geometry = None

        self.bind('<Configure>', lambda e: self._redraw())
        self.bind('<Motion>', self._on_motion)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Double-1>', self._on_double)

    # Public API ---------------------------------------------------------

    def set_banner(self, count, state=None):
        self._count, self._state = count, state
        self._redraw()

    def set_rows(self, rows, empty_message=""):
        self._rows, self._message, self._hover = list(rows), empty_message, None
        self._redraw()

    @property
    def accent(self):
        if self._state == 'yours':
            return self.colors['ally']
        if self._state == 'enemy':
            return self.colors['enemy']
        return self.side_color

    # Layout -------------------------------------------------------------

    def _layout(self):
        width, height = self.winfo_width(), self.winfo_height()
        area = height - BANNER_H - HEADING_H - 6
        row_h = max(36, min(56, (area - ROW_GAP * (ROWS - 1)) // ROWS))

        columns, x = {}, width - RIGHT_PAD - 6
        for key, _, col_width, _ in reversed(COLUMNS[1:]):
            columns[key] = (x - col_width, x)
            x -= col_width
        columns['player'] = (GUTTER + 14, x - 6)
        return width, row_h, columns

    def _row_top(self, index, row_h):
        return BANNER_H + HEADING_H + index * (row_h + ROW_GAP)

    # Drawing ------------------------------------------------------------

    def _redraw(self):
        self.delete('all')
        width, row_h, columns = self._layout()
        self._geometry = (width, row_h)
        if width < 50:
            return

        self._draw_banner(width)
        self._draw_headings(columns)

        if not self._rows:
            top = BANNER_H + HEADING_H
            self.create_text(width // 2, top + (row_h + ROW_GAP) * ROWS // 2 - 10, text=self._message,
                             font=self.fonts['message'], fill=self.colors['text_muted'])
            return

        for index, row in enumerate(self._rows[:ROWS + 1]):
            self._draw_row(index, row, width, row_h, columns)
        self._draw_parties(row_h)

    def _draw_banner(self, width):
        accent = self.accent
        bar_h = BANNER_H - 6
        self.create_rectangle(0, 0, width, bar_h, fill=accent, outline='')
        title_id = self.create_text(14, bar_h // 2, text=self.title, anchor='w',
                                    font=self.fonts['banner'], fill=DARK_TEXT)
        x = self.bbox(title_id)[2] + 12

        # Count in a slanted dark chip
        self.create_polygon(x + 4, 6, x + 34, 6, x + 30, bar_h - 6, x, bar_h - 6, fill=DARK_TEXT, outline='')
        self.create_text(x + 17, bar_h // 2, text=str(self._count), font=self.fonts['chip'], fill=accent)

        if self._state == 'yours':
            self.create_text(width - 14, bar_h // 2, text="YOUR TEAM", anchor='e',
                             font=self.fonts['chip'], fill=DARK_TEXT)

    def _draw_headings(self, columns):
        y = BANNER_H + HEADING_H // 2 - 2
        for key, heading, _, anchor in COLUMNS:
            x0, x1 = columns[key]
            x = x0 if anchor == 'w' else (x0 + x1) // 2
            self.create_text(x, y, text=heading, anchor=anchor if anchor == 'w' else 'center',
                             font=self.fonts['heading'], fill=self.colors['text_muted'])

    def _draw_row(self, index, row, width, row_h, columns):
        colors = self.colors
        top = self._row_top(index, row_h)
        bottom = top + row_h
        mid = top + row_h // 2
        x0, x1 = GUTTER, width - RIGHT_PAD
        compact = row_h < 46

        self.create_rectangle(x0, top, x1, bottom, fill=colors['row'], outline='', tags=(f'card{index}',))

        kind = row.get('kind')
        if kind == 'you':
            self._draw_corner_brackets(x0, top, x1, bottom, colors['you'])
        elif kind == 'incognito':
            self.create_rectangle(x0, top, x0 + 3, bottom, fill=colors['hidden_indicator'], outline='')

        self._draw_player_cell(row, columns['player'], top, row_h, compact)
        self._draw_rank(row.get('rank'), columns['rank'], mid)
        self._draw_rank(row.get('peak'), columns['peak'], mid)

        level_x = sum(columns['level']) // 2
        self.create_text(level_x, mid, text=row.get('level', '—'),
                         font=self.fonts['muted' if row.get('level_muted') else 'stat'],
                         fill=colors['text_muted' if row.get('level_muted') else 'text_primary'])

        self._draw_stat(row.get('win'), columns['win'], mid, (60, 53, 45))
        self._draw_stat(row.get('kd'), columns['kd'], mid, (1.3, 1.05, 0.9),
                        font=self.fonts['kd_small' if compact else 'kd'])
        self._draw_stat(row.get('hs'), columns['hs'], mid, (28, 22, 15))
        self._draw_info(row.get('info') or [], columns['info'], mid)

    def _draw_corner_brackets(self, x0, top, x1, bottom, color, size=9):
        for x, y, dx, dy in ((x0, top, 1, 1), (x1, top, -1, 1), (x0, bottom, 1, -1), (x1, bottom, -1, -1)):
            self.create_line(x, y + dy * size, x, y, x + dx * size, y, fill=color, width=2)

    def _draw_player_cell(self, row, bounds, top, row_h, compact):
        colors = self.colors
        x, x_end = bounds
        kind = row.get('kind')
        name_color = {'you': colors['you'], 'incognito': colors['hidden_indicator']}.get(kind, colors['text_primary'])
        name_font = self.fonts['name_small' if compact else 'name']
        tag_font = self.fonts['tag']

        baseline = top + int(row_h * (0.58 if not compact else 0.6))
        name = row.get('name', '')
        if kind == 'you':
            name = f"★ {name}"
        tag = row.get('tag', '')
        tag_text = f"#{tag}" if tag else ''

        available = x_end - x
        tag_w = tag_font.measure(tag_text) if tag_text else 0
        if name_font.measure(name) + 5 + tag_w > available:
            if tag_text and available - tag_w - 5 >= 70:
                name = self._fit(name, name_font, available - tag_w - 5)
            else:
                tag_text, name = '', self._fit(name, name_font, available)

        name_id = self.create_text(x, baseline, text=name, anchor='sw', font=name_font, fill=name_color)
        if tag_text:
            self.create_text(self.bbox(name_id)[2] + 4, baseline - 2, text=tag_text, anchor='sw',
                             font=tag_font, fill=colors['text_muted'])

        self.create_text(x, baseline + 1, text=row.get('agent', '—'), anchor='nw',
                         font=self.fonts['agent'], fill=colors['text_secondary'])

    def _draw_rank(self, rank, bounds, mid):
        x = bounds[0]
        color = rank_color(rank)
        if not color:
            self.create_text(x + 18, mid, text=rank or '—', anchor='w',
                             font=self.fonts['muted'], fill=self.colors['text_muted'])
            return

        # Small two-tone gem in the tier colour
        cx, r = x + 6, 7
        self.create_polygon(cx, mid - r, cx + r - 1, mid, cx, mid + r, cx - r + 1, mid, fill=color, outline='')
        inner = blend(color, self.colors['row'], 0.55)
        self.create_polygon(cx, mid - 3, cx + 2, mid, cx, mid + 3, cx - 2, mid, fill=inner, outline='')
        self.create_text(x + 18, mid, text=rank.upper(), anchor='w', font=self.fonts['rank'], fill=color)

    def _draw_stat(self, stat, bounds, mid, thresholds, font=None):
        text, value = stat if stat else ('—', None)
        x = sum(bounds) // 2
        if value is None:
            self.create_text(x, mid, text=text, font=self.fonts['muted'], fill=self.colors['text_muted'])
            return

        hot, good, low = thresholds
        if value >= hot:
            color = self.accent
        elif value >= good:
            color = self.colors['you']
        elif value < low:
            color = self.colors['text_secondary']
        else:
            color = self.colors['text_primary']
        self.create_text(x, mid, text=text, font=font or self.fonts['stat'], fill=color)

    def _draw_info(self, marks, bounds, mid):
        if not marks:
            return
        font = self.fonts['stat']
        gap = 6
        total = sum(font.measure(text) for text, _ in marks) + gap * (len(marks) - 1)
        x = (sum(bounds) - total) // 2
        for text, color in marks:
            self.create_text(x, mid, text=text, anchor='w', font=font, fill=color)
            x += font.measure(text) + gap

    def _draw_parties(self, row_h):
        """A coloured strip left of each run of players who queued together"""
        index = 0
        rows = self._rows[:ROWS + 1]
        while index < len(rows):
            party = rows[index].get('party')
            end = index
            while party and end + 1 < len(rows) and (rows[end + 1].get('party') or (None,))[0] == party[0]:
                end += 1
            if party and end > index:
                self._draw_party_strip(party, end - index + 1, self._row_top(index, row_h),
                                       self._row_top(end, row_h) + row_h)
            index = end + 1

    def _draw_party_strip(self, party, size, top, bottom):
        number, confirmed, _ = party
        color = PARTY_COLORS[(number - 1) % len(PARTY_COLORS)]
        label = PARTY_LABELS.get(size, f"{size}-STACK")
        x0, x1 = 2, GUTTER - 5
        mid_x, mid_y = (x0 + x1) / 2, (top + bottom) / 2

        if confirmed:
            self.create_rectangle(x0, top, x1, bottom, fill=color, outline='')
            text_color = DARK_TEXT
        else:
            # Likely party (from recent matches): outline only
            self.create_rectangle(x0, top, x1, bottom, outline=color, width=1, dash=(3, 2))
            text_color, label = color, f"{label}?"
        self.create_text(mid_x, mid_y, text=label, angle=90, font=self.fonts['party'], fill=text_color)

    @staticmethod
    def _fit(text, font, width):
        if font.measure(text) <= width:
            return text
        while text and font.measure(text + "…") > width:
            text = text[:-1]
        return text + "…"

    # Mouse --------------------------------------------------------------

    def _row_at(self, y):
        if not self._rows or not self._geometry:
            return None
        _, row_h = self._geometry
        offset = y - BANNER_H - HEADING_H
        if offset < 0:
            return None
        index, within = divmod(offset, row_h + ROW_GAP)
        if within > row_h or index >= min(len(self._rows), ROWS + 1):
            return None
        return int(index)

    def _set_hover(self, index):
        if index == self._hover:
            return
        if self._hover is not None:
            self.itemconfig(f'card{self._hover}', fill=self.colors['row'])
        if index is not None:
            self.itemconfig(f'card{index}', fill=self.colors['row_hover'])
        self._hover = index

    def _on_motion(self, event):
        index = self._row_at(event.y)
        self._set_hover(index)
        if self.on_hover:
            self.on_hover(self._rows[index]['player'] if index is not None else None, event)

    def _on_leave(self, event):
        self._set_hover(None)
        if self.on_leave:
            self.on_leave()

    def _on_double(self, event):
        index = self._row_at(event.y)
        if index is not None and self.on_open:
            self.on_open(self._rows[index]['player'])
