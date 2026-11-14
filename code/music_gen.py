import numpy as np, wave, subprocess
sr=44100; import sys; total=float(sys.argv[1]); n=int(total*sr); out=np.zeros(n)
bpm=120; beat=60/bpm
mid=lambda m:440*2**((m-69)/12)
def add(sig,start,amp):
    i0=int(start*sr); m=min(len(sig),n-i0)
    if m>0: out[i0:i0+m]+=amp*sig[:m]
def pluck(f,dur,dec=4):
    t=np.arange(int(dur*sr))/sr
    return (np.sin(2*np.pi*f*t)+.5*np.sin(4*np.pi*f*t)*np.exp(-3*t)+.25*np.sin(6*np.pi*f*t)*np.exp(-6*t))*np.exp(-dec*t)*np.minimum(1,t/.004)
def whistle(f,dur):
    t=np.arange(int(dur*sr))/sr
    vib=np.sin(2*np.pi*5.5*t)*0.004*np.minimum(1,t/0.15)
    env=np.minimum(1,t/0.03)*np.minimum(1,(dur-t)/0.06)
    return np.sin(2*np.pi*f*t*(1+vib))*env
def kick():
    t=np.arange(int(.25*sr))/sr
    return np.sin(2*np.pi*(50+90*np.exp(-30*t))*t)*np.exp(-12*t)
rng=np.random.default_rng(2)
def clap():
    m=int(.12*sr); t=np.arange(m)/sr
    return rng.standard_normal(m)*np.exp(-30*t)
def hat():
    m=int(.04*sr); t=np.arange(m)/sr
    return rng.standard_normal(m)*np.exp(-90*t)
chords=[[60,64,67],[67,71,74],[69,72,76],[65,69,72]]
bass=[36,43,45,41]
# whistle melody: (midi, beats) per 2-bar phrase, repeated
mel=[(72,1),(74,.5),(76,1.5),(79,1),(76,1),(74,.5),(72,.5),(74,2),(0,1),
     (76,1),(77,.5),(79,1.5),(81,1),(79,1),(76,.5),(74,.5),(72,2),(0,1)]
bars=int(total/(beat*4))+1
for b in range(bars):
    t0=b*beat*4; ch=chords[b%4]
    for k in range(8):  # bouncy offbeat ukulele strum
        st=t0+k*beat/2
        for j,nn in enumerate(ch): add(pluck(mid(nn+12),.4,7),st+j*.008,.09 if k%2 else .06)
    for k in (0,2.5): add(pluck(mid(bass[b%4]),beat*1.5,2.5),t0+k*beat,.4)
    for k in range(4):
        if b>=1: add(kick(),t0+k*beat,.55)
        if b>=1 and k in (1,3): add(clap(),t0+k*beat,.18)
    for k in range(8):
        if b>=1: add(hat(),t0+k*beat/2+beat/4,.07)
# melody starts bar 2
t=beat*4*2
while t<total-2:
    for nn,bl in mel:
        if nn: add(whistle(mid(nn),bl*beat*.95),t,.16)
        t+=bl*beat
fade=int(1.5*sr); out[-fade:]*=np.linspace(1,0,fade)
out=np.tanh(out/np.max(np.abs(out))*1.4)*0.85
with wave.open(sys.argv[2],"w") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype(np.int16).tobytes())
