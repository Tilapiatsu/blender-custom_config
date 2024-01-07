def H264_in_MP4(scene):
    is_ntsc = (scene.render.fps != 25)

    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"

    if is_ntsc:
        scene.render.ffmpeg.gopsize = 18
    else:
        scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.use_max_b_frames = False

    scene.render.ffmpeg.video_bitrate = 6000
    scene.render.ffmpeg.maxrate = 9000
    scene.render.ffmpeg.minrate = 0
    scene.render.ffmpeg.buffersize = 224 * 8
    scene.render.ffmpeg.packetsize = 2048
    scene.render.ffmpeg.muxrate = 10080000

def Xvid(scene):
    is_ntsc = (scene.render.fps != 25)

    scene.render.ffmpeg.format = "AVI"
    scene.render.ffmpeg.codec = "MPEG4"

    if is_ntsc:
        scene.render.ffmpeg.gopsize = 18
    else:
        scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.use_max_b_frames = False

    scene.render.ffmpeg.video_bitrate = 6000
    scene.render.ffmpeg.maxrate = 9000
    scene.render.ffmpeg.minrate = 0
    scene.render.ffmpeg.buffersize = 224 * 8
    scene.render.ffmpeg.packetsize = 2048
    scene.render.ffmpeg.muxrate = 10080000

def WebM_VP9(scene):
    scene.render.ffmpeg.format = "WEBM"
    scene.render.ffmpeg.codec = "VP9"
    scene.render.ffmpeg.audio_codec = "OPUS"
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.use_max_b_frames = False

def Ogg_Theora(scene):
    is_ntsc = (scene.render.fps != 25)

    scene.render.ffmpeg.format = "OGG"
    scene.render.ffmpeg.codec = "THEORA"

    if is_ntsc:
        scene.render.ffmpeg.gopsize = 18
    else:
        scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.use_max_b_frames = False

    scene.render.ffmpeg.video_bitrate = 6000
    scene.render.ffmpeg.maxrate = 9000
    scene.render.ffmpeg.minrate = 0
    scene.render.ffmpeg.buffersize = 224 * 8
    scene.render.ffmpeg.packetsize = 2048
    scene.render.ffmpeg.muxrate = 10080000

def H264_in_Matroska(scene):
    is_ntsc = (scene.render.fps != 25)

    scene.render.ffmpeg.format = "MKV"
    scene.render.ffmpeg.codec = "H264"

    if is_ntsc:
        scene.render.ffmpeg.gopsize = 18
    else:
        scene.render.ffmpeg.gopsize = 15

    scene.render.ffmpeg.video_bitrate = 6000
    scene.render.ffmpeg.maxrate = 9000
    scene.render.ffmpeg.minrate = 0
    scene.render.ffmpeg.buffersize = 224 * 8
    scene.render.ffmpeg.packetsize = 2048
    scene.render.ffmpeg.muxrate = 10080000

def H264_in_Matroska_for_scrubbing(scene):
    scene.render.ffmpeg.format = "MKV"
    scene.render.ffmpeg.codec = "H264"

    scene.render.ffmpeg.gopsize = 1
    scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
    scene.render.ffmpeg.use_max_b_frames = True
    scene.render.ffmpeg.max_b_frames = 0