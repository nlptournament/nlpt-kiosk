from multiprocessing import Process

metrics_exporter_process = None


def start_metrics_exporter():
    from elements import Setting
    global metrics_exporter_process

    def metrics_exporter_function():
        import cherrypy
        from elements import Screen, ScreenTemplate
        from endpoints import PlayercountsEndpoint

        class Metrics():
            @cherrypy.expose()
            def index(self):
                lines = list()

                # Games played according to Discord
                lines.append('# HELP discord_game_played_count Number of Players playing a Game regarding to Discord')
                lines.append('# TYPE discord_game_played_count gauge')
                metrics_covered = list()
                for template in ScreenTemplate.all(filter={'key': 'player-counts'}):
                    for screen in Screen.all(filter={'template_id': template['_id']}):
                        if screen['variables'].get('src_discord', False):
                            guild = screen['variables'].get('guild', '')
                            role = screen['variables'].get('role', '')
                            if f'{guild}_{role}' not in metrics_covered:
                                metrics_covered.append(f'{guild}_{role}')
                                for c in PlayercountsEndpoint.discord_counts(guild=guild, role=role):
                                    lines.append(f'discord_game_played_count{{guild="{guild}",role="{role}",game="{c["game"]}"}} {c["count"]}')

                cherrypy.response.headers['Cache-Control'] = 'no-cache'
                cherrypy.response.headers['Content-Type'] = 'text/plain; version=0.0.4'
                return '\n'.join(lines)

        metrics_port = Setting.value('metrics_port')
        cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': metrics_port})
        cherrypy.quickstart(Metrics(), '/metrics')

    metrics_enabled = Setting.value('metrics_enabled')
    if metrics_enabled and metrics_exporter_process is None:
        metrics_exporter_process = Process(target=metrics_exporter_function, daemon=True)
        metrics_exporter_process.start()
