
import os
import math
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

os.makedirs("frames", exist_ok=True)

W, H = 720, 1280
FPS = 24
DURATION = 18

cores = [
    ("VERMELHO", (255, 75, 85), "O vermelho é lindo!"),
    ("AZUL", (55, 130, 255), "O azul é a cor do céu!"),
    ("VERDE", (50, 190, 105), "O verde está nas plantas!"),
    ("AMARELO", (255, 195, 35), "O amarelo brilha como o sol!")
]

try:
    titulo = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
    )
    letra = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64
    )
    texto = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32
    )
except OSError:
    titulo = letra = texto = ImageFont.load_default()

# Criar as cenas animadas
for i in range(FPS * DURATION):
    t = i / FPS
    cena = min(int(t / (DURATION / 4)), 3)
    nome, cor, frase = cores[cena]

    img = Image.new("RGB", (W, H), (255, 247, 224))
    d = ImageDraw.Draw(img)

    d.text((W // 2, 100), "APRENDENDO AS CORES",
           font=titulo, fill=(90, 65, 130), anchor="mm")

    x = int(W / 2 + 45 * math.sin(t * 2))
    y = 500 + int(18 * math.sin(t * 4))
    r = 155

    d.ellipse((x-r, y-r, x+r, y+r), fill=cor)
    d.text((W // 2, 790), nome, font=letra,
           fill=cor, anchor="mm")
    d.text((W // 2, 900), frase, font=texto,
           fill=(55, 55, 75), anchor="mm")

    # Pequenas estrelas decorativas
    for sx, sy in [(100, 300), (600, 350),
                   (120, 1050), (590, 1080)]:
        d.ellipse((sx-10, sy-10, sx+10, sy+10),
                  fill=(255, 190, 65))

    img.save(f"frames/{i:04d}.png")

# Criar a narração em português
falas = "Vamos aprender as cores! Vermelho! O vermelho é lindo! " \
        "Azul! O azul é a cor do céu! " \
        "Verde! O verde está nas plantas! " \
        "Amarelo! O amarelo brilha como o sol! Muito bem!"

subprocess.run([
    "espeak-ng", "-v", "pt-br", "-s", "145",
    "-w", "narracao.wav", falas
], check=True)

# Criar uma música instrumental original e simples
sr = 22050
dur = DURATION
t = np.arange(sr * dur) / sr
notas = [261.63, 329.63, 392.00, 329.63,
         293.66, 349.23, 440.00, 349.23]
musica = np.zeros(len(t))

for j, inicio in enumerate(np.arange(0, dur, 0.5)):
    fim = min(inicio + 0.48, dur)
    a = int(inicio * sr)
    b = int(fim * sr)
    tt = np.arange(b-a) / sr
    freq = notas[j % len(notas)]
    envelope = np.minimum(tt / 0.04, 1) * np.maximum(
        0, np.minimum((fim-inicio-tt) / 0.08, 1)
    )
    musica[a:b] += 0.16 * np.sin(2*np.pi*freq*tt) * envelope

musica = np.clip(musica, -1, 1)
audio = (musica * 32767).astype(np.int16)

with wave.open("musica.wav", "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sr)
    f.writeframes(audio.tobytes())

# Montar o vídeo MP4 com narração e música
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", "frames/%04d.png",
    "-i", "narracao.wav",
    "-i", "musica.wav",
    "-filter_complex",
    "[1:a]volume=1.0[voz];"
    "[2:a]volume=0.18[fundo];"
    "[voz][fundo]amix=inputs=2:duration=longest[audio]",
    "-map", "0:v", "-map", "[audio]",
    "-t", str(DURATION),
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-shortest",
    "video_cores.mp4"
], check=True)

print("Vídeo criado: video_cores.mp4")
