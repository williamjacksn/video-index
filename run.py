import notch
import video_index.app

log = notch.make_log('video-index.entrypoint')

if __name__ == '__main__':
    video_index.app.main()
