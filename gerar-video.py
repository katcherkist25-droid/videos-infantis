
import os
import math
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = 12
DURATION = 150
SR = 22050

os.makedirs("frames", exist_ok=True)
os.makedirs("audio", exist_ok=True)

CENAS = [
    (0, 12, "Bem-vindos ao bosque encantado!", "ABERTURA"),
    (12, 30, "Oi, amiguinhos! Eu sou a Lili. Que cor e esta?", "CESTO"),
    (30, 60, "Vermelho! Uma maca, uma flor e uma casinha. Um, dois, tres!", "VERMELHO"),
    (60, 80, "Cores, cores vamos cantar! Vermelho, amarelo, azul a brilhar!", "REFRAO"),
    (80, 100, "Olha o amarelo do sol e o azul do ceu!", "AMARELO_AZUL"),
    (100, 115, "Onde esta o objeto verde? Pense e responda!", "JOGO_VERDE"),
    (115, 140, "Vamos contar juntos: um, dois, tres, quatro, cinco!", "CONTAGEM"),
    (140, 150, "Aprendemos as cores! Explore a natureza. Ate a proxima!", "FINAL")
]

def fonte(tamanho, bold=False):
    caminho = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        return ImageFont.truetype(caminho, tamanho)
    except OSError:
        return ImageFont.load_default()

def escrever(draw, xy, texto, tamanho=30, cor=(50, 55, 65), bold=False):
    draw.text(xy, texto, font=fonte(tamanho, bold), fill=cor, anchor="mm")

def animal(draw, x, y, nome, cor, escala=1):
    r = int(48 * escala)
    draw.ellipse((x-r, y-r, x+r, y+r), fill=cor, outline=(90, 75, 70), width=3)
    draw.ellipse((x-r*0.8, y-r*1.35, x-r*0.15, y-r*0.45), fill=cor)
    draw.ellipse((x+r*0.15, y-r*1.35, x+r*0.8, y-r*0.45), fill=cor)
    for dx in [-17, 17]:
        draw.ellipse((x+dx-10, y-15, x+dx+10, y+10), fill="white")
        draw.ellipse((x+dx-4, y-8, x+dx+4, y+5), fill=(35, 35, 45))
    draw.arc((x-15, y, x+15, y+23), 0, 180, fill=(80, 50, 45), width=3)
    escrever(draw, (x, y+r+24), nome, 22, bold=True)

def criar_cena(t, nome):
    img = Image.new("RGB", (W, H), (255, 242, 218))
    d = ImageDraw.Draw(img)

    # Ceu e gramado
    d.rectangle((0, 430, W, H), fill=(183, 218, 151))
    d.ellipse((80, 55, 185, 160), fill=(255, 211, 85))

    # Arvores do bosque
    for x, y, r in [(100, 320, 100), (250, 320, 115),
                    (1030, 320, 120), (1180, 340, 95)]:
        d.rectangle((x-15, y, x+15, 510), fill=(150, 108, 75))
        d.ellipse((x-r, y-r, x+r, y+r), fill=(132, 190, 126))

    # Quatro amigos
    animal(d, 300, 365+int(7*math.sin(t*2)), "Lili", (241, 151, 102))
    animal(d, 490, 390+int(5*math.sin(t*2)), "Tito", (139, 157, 91), .9)
    animal(d, 680, 355+int(9*math.sin(t*3)), "Bia", (100, 190, 237), .75)
    animal(d, 880, 375+int(6*math.sin(t*2)), "Nino", (153, 169, 181), 1.1)

    objetos = {
        "CESTO": [("MACA", (230, 65, 70)), ("SOL", (255, 205, 50)), ("BOLA", (70, 130, 240))],
        "VERMELHO": [("1", (230, 65, 70)), ("2", (230, 65, 70)), ("3", (230, 65, 70))],
        "REFRAO": [("VERMELHO", (230, 65, 70)), ("AMARELO", (255, 205, 50)), ("AZUL", (70, 130, 240))],
        "AMARELO_AZUL": [("AMARELO", (255, 205, 50)), ("AZUL", (70, 130, 240))],
        "JOGO_VERDE": [("VERDE?", (70, 170, 90))],
        "CONTAGEM": [(str(i), (255, 255, 255)) for i in range(1, 6)],
        "FINAL": [("VERMELHO", (230, 65, 70)), ("AMARELO", (255, 205, 50)), ("AZUL", (70, 130, 240)), ("VERDE", (70, 170, 90))]
    }

    itens = objetos.get(nome, [])
    inicio = W//2 - (len(itens)-1)*90
    for i, (rotulo, cor) in enumerate(itens):
        x = inicio + i*180
        y = 555 + int(8*math.sin(t*3+i))
        d.rounded_rectangle((x-65, y-38, x+65, y+38), radius=15, fill=cor)
        escrever(d, (x, y), rotulo, 22)

    fala = next((f for a, b, f, n in CENAS if a <= t < b), "")
    d.rounded_rectangle((30, 625, W-30, 700), radius=16, fill=(255, 255, 255))
    escrever(d, (W//2, 662), fala, 25)
    if nome == "ABERTURA":
        escrever(d, (W//2, 85), "A CANCAO DAS CORES NO BOSQUE", 42, (100, 75, 130), True)
    return img

# Desenhar os quadros
for i in range(FPS * DURATION):
    t = i / FPS
    nome = next((n for a, b, f, n in CENAS if a <= t < b), "FINAL")
    criar_cena(t, nome).save(f"frames/{i:05d}.png")

# Criar uma fala em portugues para cada cena
audio_final = np.zeros(SR * DURATION, dtype=np.float64)

for i, (inicio, fim, fala, nome) in enumerate(CENAS):
    caminho = f"audio/fala_{i}.wav"
    subprocess.run(["espeak-ng", "-v", "pt-br", "-s", "145", "-w", caminho, fala], check=True)

    with wave.open(caminho, "rb") as w:
        voz = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
        taxa = w.getframerate()
        canais = w.getnchannels()

    if canais > 1:
        voz = voz.reshape(-1, canais).mean(axis=1)
    if taxa != SR:
        raise RuntimeError("A taxa de audio da narracao nao corresponde.")

    pos = int((inicio + 0.5) * SR)
    fim_pos = min(pos + len(voz), len(audio_final))
    audio_final[pos:fim_pos] += voz[:fim_pos-pos] * 0.7

# Melodia instrumental simples
musica = np.zeros_like(audio_final)
notas = [261.63, 329.63, 392.00, 329.63, 293.66, 349.23, 440.00, 349.23]

for j, inicio in enumerate(np.arange(0, DURATION, 0.4)):
    a = int(inicio * SR)
    b = min(int((inicio+0.36)*SR), len(musica))
    tt = np.arange(b-a) / SR
    envelope = np.minimum(tt/0.03, 1) * np.maximum(0, np.minimum((0.36-tt)/0.05, 1))
    musica[a:b] += 1800 * np.sin(2*np.pi*notas[j % len(notas)]*tt) * envelope

mix = audio_final + musica
pico = max(np.max(np.abs(mix)), 32767)
mix = np.clip(mix / pico * 30000, -32767, 32767).astype(np.int16)

with wave.open("audio_final.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(mix.tobytes())

# Exportar MP4
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", "frames/%05d.png", "-i", "audio_final.wav",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-pix_fmt", "yuv420p", "-c:a", "aac",
    "-b:a", "128k", "-t", str(DURATION),
    "-movflags", "+faststart",
    "cancao_das_cores_no_bosque.mp4"
], check=True)

print("Video criado: cancao_das_cores_no_bosque.mp4")
