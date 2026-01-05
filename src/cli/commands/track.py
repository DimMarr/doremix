import typer, yt_dlp, vlc, time

from services.track import get_track

app = typer.Typer()

player: vlc.MediaPlayer | None = None
instance: vlc.Instance | None = None

@app.command(help="Play a track.")
def play(id :int):
    # Get Youtube Audio URL (e.g. : https://rr5---sn-25glenlz.googlevideo.com/videoplayback?expire=1767307324&ei=3KNWaevjDLaDi9oP9K7GGQ&ip=46.193.64.92&id=o-AInmKMypqBJ-SjuQMDidGmiDlItgIKIxZP2TdcWY2P-E&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&cps=649&met=1767285724%2C&mh=7c&mm=31%2C26&mn=sn-25glenlz%2Csn-h5q7knes&ms=au%2Conr&mv=m&mvi=5&pl=19&rms=au%2Cau&initcwndbps=2622500&bui=AYUSA3BPwKzgK-pgmhJTwJZmeK9uksAwitqB-RhVi_TVdNn-PiJsQct9YshZBLvWk8iMQy3u-aT9k7wd&spc=wH4QqyPrpaLaMaeLGA&vprv=1&svpuc=1&mime=audio%2Fwebm&rqh=1&gir=yes&clen=3433755&dur=213.061&lmt=1766955883819090&mt=1767285206&fvip=4&keepalive=yes&fexp=51552689%2C51565115%2C51565681%2C51580968&c=ANDROID&txp=5532534&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAL3b_GhoJMVz09HRhu9TlU8lq0wVFxwXTiQzm5Nq_EOWAiEA6Z9p_HF54q8as2Xhu7O3AMPSX4iVLKPC75aGXjKvEpo%3D&lsparams=cps%2Cmet%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRgIhAKUZCUVXrR0_CgfWncbclVzWmdoEXS9-DxaOlacQNo1RAiEA4Wdy6c1iOQaSg3euXXVyqfw1IURr0vvkTB9kCSxgLC8%3D)    
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(get_track(id).youtubeLink)
        audio_url = info['url']

    # Stream with VLC
    instance = vlc.Instance('--quiet')
    player = instance.media_player_new()
    media = instance.media_new(audio_url)
    player.set_media(media)
    player.play()

    print("Waiting for VLC to start...")
    while not player.is_playing():
        time.sleep(0.1)
    print("Playing!")
    
    # Keep the script running while audio plays
    try:
        while player.is_playing():
            time.sleep(1)
    except KeyboardInterrupt:
        player.stop()


