class Game:
    def __init__(self, matchID, map_name, session_state, party=None, players=None, localPlayer=None):
        self.matchID = matchID
        self.map_name = map_name
        self.session_state = session_state
        self.players = players or []
        self.localPlayer = localPlayer
        self.teamPlayers = self.find_team_players(self.localPlayer, self.players) if self.localPlayer else []
        self.partyPlayers = self.find_party_members(party) if party else []

    def find_hidden_names(self, players):
        self.found = False
        print("=" * 50)
        print("HIDDEN PLAYERS DETECTED:")
        print("=" * 50)
        
        for player in players:
            if player.incognito:
                self.found = True
                print(f"🔍 {player.full_name} - {player.team} ({player.agent})")
        
        if not self.found:
            print("✅ No hidden names found in this match")
        print("=" * 50)

    # Progress bar credit: https://stackoverflow.com/users/2206251/
    @staticmethod
    def _progressBar(iterable, prefix='', suffix='', decimals=1, length=50, fill='█', printEnd="\r"):
        total = len(iterable)
        
        def printProgressBar(iteration):
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        
        printProgressBar(0)
        
        for i, item in enumerate(iterable):
            yield item
            printProgressBar(i + 1)
        
        print()

    def find_streamers(self, players, twitchReqDelay, skipTeamPlayers, skipPartyPlayers):
        self.streamers = []
        self.social_media = []
        print("\n🔴 Checking for streamers and social media...")
        
        for player in self._progressBar(
            players, 
            prefix='Scanning:', 
            suffix='Complete', 
            length=30
        ):
            if skipTeamPlayers and player in self.teamPlayers:
                continue
            if skipPartyPlayers and player.puuid in self.partyPlayers:
                continue
            
            # Check all platforms
            found_platforms = player.check_all_platforms(twitchReqDelay)
            
            for platform_info in found_platforms:
                platform = platform_info['platform']
                username = platform_info['username']
                url = platform_info['url']
                status = platform_info['status']
                
                if platform in ['twitch', 'youtube', 'kick'] and status == 'live':
                    self.streamers.append(f"{platform.title()}: {url}")
                else:
                    self.social_media.append(f"{platform.title()}: {url}")
        
        print("\n" + "=" * 60)
        
        # Display live streamers
        if len(self.streamers) > 0:
            print("🔴 LIVE STREAMERS FOUND:")
            for streamer in self.streamers:
                print(f"📺 {streamer}")
        
        # Display social media profiles
        if len(self.social_media) > 0:
            if len(self.streamers) > 0:
                print("\n📱 SOCIAL MEDIA PROFILES FOUND:")
            else:
                print("📱 SOCIAL MEDIA PROFILES FOUND:")
            for profile in self.social_media:
                print(f"🔗 {profile}")
        
        if len(self.streamers) == 0 and len(self.social_media) == 0:
            print("❌ No streamers or social media profiles found")
        
        print("=" * 60)

    def find_team_players(self, localPlayer, players):
        team_players = []
        for player in players:
            if player.team == localPlayer.team:
                team_players.append(player)
        return team_players

    def find_party_members(self, party):
        members = []
        if party and 'Members' in party:
            for member in party['Members']:
                members.append(member['Subject'].lower())
        return members