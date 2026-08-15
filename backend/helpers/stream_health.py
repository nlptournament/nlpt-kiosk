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
    while True:
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
    url = media['src']
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=nb_frames',
                '-of', 'json',
                url,
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            # ffprobe failed → stream is inactive
            _update_active_status(media, False)
            return

        import json as json_lib
        data = json_lib.loads(result.stdout)
        streams = data.get('streams', [])

        # Active if has frames (live stream actively producing)
        active = any(s.get('nb_frames', 0) > 0 for s in streams)
        _update_active_status(media, active)

    except subprocess.TimeoutExpired:
        # Timeout → stream is inactive
        _update_active_status(media, False)
    except Exception as e:
        print(f'error checking stream {media["_id"]}: {e}')
        _update_active_status(media, False)


def _update_active_status(media, active):
    """Update media health status in global registry and broadcast via WSS if changed."""
    from helpers.wss import transmit_media_health

    current_active = Media._health_registry.get(media['_id'], None)

    if current_active != active:
        Media._health_registry[media['_id']] = active
        transmit_media_health(media)
