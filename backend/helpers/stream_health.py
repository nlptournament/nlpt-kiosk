import time
import subprocess
from multiprocessing import Process
from elements import Media


worker_process = None


def start_stream_health_worker():
    global worker_process
    if worker_process is None:
        worker_process = Process(target=_health_checker, daemon=True)
        worker_process.start()


def _health_checker():
    from elements import Setting
    while True:
        if Setting.value('participant_interface'):
            try:
                for media in Media.all():
                    # Only check web URL streams (type=3, src_type=0)
                    if media['type'] == 3 and media['src_type'] == 0:
                        _check_stream(media)
            except Exception as e:
                print(f'error on stream health check: {e}')
        time.sleep(10)


def _check_stream(media):
    """Check if a stream is actively producing data using ffprobe."""
    from helpers.wss import transmit_media_health
    url = media['src']
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-show_format',
                '-of', 'json',
                url,
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            # ffprobe failed → stream is inactive
            transmit_media_health(media, False)
            return

        import json as json_lib
        data = json_lib.loads(result.stdout)

        # Active if has steams
        active = data.get('format', {}).get('nb_streams', 0) > 0
        transmit_media_health(media, active)

    except subprocess.TimeoutExpired:
        # Timeout → stream is inactive
        transmit_media_health(media, False)
    except Exception as e:
        print(f'error checking stream {media["_id"]}: {e}')
        transmit_media_health(media, False)
