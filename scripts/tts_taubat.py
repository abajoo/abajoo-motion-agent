"""Generate Indonesian male narration with open-source arboTTS."""
from pathlib import Path
import subprocess
import wave
from arbotts import ArboTTS

TEXT = """Kita semua pernah salah. Bahkan terkadang, mengulangi kesalahan yang sama.
Hingga suatu hari, hati terasa begitu berat. Seolah tak ada lagi jalan pulang.
Namun, sebesar apa pun dosa kita, jangan pernah berputus asa dari rahmat Allah.
Karena Allah tak menunggu kita sempurna. Dia membuka pintu taubat bagi hamba yang ingin kembali.
Selama napas masih berembus, kesempatan untuk berubah masih ada.
At-Tawwab. Allah Maha Penerima Taubat. Pulanglah kepada-Nya."""

out = Path("output")
out.mkdir(exist_ok=True)
voice = __import__("os").environ.get("VOICE", "danu").lower()
if voice not in {"danu", "bimo"}:
    raise ValueError("VOICE must be danu or bimo")
wav = out / f"taubat_{voice}_raw.wav"
tts = ArboTTS(tier="standard")
tts.speak(text=TEXT, output_file=str(wav), speaker=voice, lang="id", speed=0.95)
with wave.open(str(wav)) as audio:
    duration = audio.getnframes() / audio.getframerate()
print(f"Generated WAV duration: {duration:.2f} seconds")
# Keep the narration complete: fit into 29.5 s only if required, preserving pitch.
tempo = max(0.5, min(2.0, duration / 29.5))
if duration / 29.5 > 2.0:
    raise RuntimeError("Narration too long to fit naturally into 30 seconds; shorten the script")
target = out / f"taubat_{voice}_30s.mp3"
subprocess.run([
    "ffmpeg", "-y", "-i", str(wav),
    "-af", f"atempo={tempo:.6f},apad=pad_dur=2,atrim=0:30,afade=t=out:st=29.4:d=0.6",
    "-codec:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", str(target)
], check=True)
subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1", str(target)], check=True)
print(f"Created {target}")
