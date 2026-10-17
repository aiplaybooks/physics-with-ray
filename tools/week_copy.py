"""Haftalık içerik metinleri (hook, caption gövdesi, 3 konu etiketi, ilk yorum) ve slot planı.

python tools/week_copy.py patch      # queue.json'daki 3-8. videoların metnini günceller
python tools/week_copy.py enqueue    # 9-23. videoları + kapakları kuyruğa ekler (queue/ klasörüne kopyalar)
python tools/week_copy.py plan       # 21 yayının tarih/saat planını yazdırır (FB elle planlama için)

Etiket mantığı: IG artık en fazla 5 etiket tutuyor; Mosseri'ye göre etiketler tek başına erişimi artırmıyor,
asıl iş caption anahtar kelimelerinde. Bu yüzden her gönderi = 2 çekirdek (#physics #physicsfacts) + 3 konuya özel etiket,
ve hook/gövde cümlelerinde aranabilir anahtar kelime (konu adı + 'physics') geçiyor. Gövdenin sonu 'gönder/kaydet' çağrısı
(gönderim/erişim oranı sıralama sinyali).
"""
import datetime as dt
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "vector", "cikti")
K = os.path.join(V, "kapak")

# no: (video dosyası, kapak dosyası, hook, gövde, [3 etiket], ilk yorum)
COPY = {
    3: ("", "", "Why do you lurch forward when a bus suddenly brakes? 🚌",
        "Ray explains inertia, Newton's first law of motion, with everyday examples. Send this to someone who has spilled a drink on the bus.",
        ["#inertia", "#newtonslaws", "#learnphysics"],
        "Be honest: what did you think pushed you forward, before watching? 👇"),
    4: ("", "", "Why is it harder to push a heavy cart than an empty one? 🛒",
        "Ray shows Newton's second law, F = m·a, step by step with a simple cart. Save this for your next physics test.",
        ["#newtonssecondlaw", "#forceandmotion", "#stemeducation"],
        "Quick one: same push, double the mass. What happens to the acceleration? 👇"),
    5: ("", "", "When you push a wall, does the wall push back? 🧱",
        "Ray reveals Newton's third law: forces always come in pairs. Send this to a friend who says 'that can't be true'.",
        ["#newtonsthirdlaw", "#actionreaction", "#sciencefacts"],
        "Who feels the bigger force: you or the wall? Tell us your answer 👇"),
    6: ("", "", "Where does a rolling ball's energy go when it stops? ⚡",
        "Ray follows energy as it changes form, and shows why energy is never lost: the law of conservation of energy.",
        ["#energy", "#conservationofenergy", "#learnphysics"],
        "Can you name three places the ball's energy ended up? 👇"),
    7: ("", "", "Why does a hot drink cool down but never heat up by itself? ☕",
        "Ray explains heat and temperature, and why heat always flows from hot to cold. Save this for your next coffee break.",
        ["#heattransfer", "#thermodynamics", "#sciencefacts"],
        "What's the longest your coffee has ever stayed hot? ☕👇"),
    8: ("", "", "How does electricity actually get to your lamp? 💡",
        "Ray follows the current through a simple electric circuit and shows what is really flowing in the wire. Send this to your favorite electrician.",
        ["#electricity", "#electriccircuit", "#stemeducation"],
        "Guess first: what is actually moving inside the wire? Then check the video 👇"),
    9: ("video9_waves.mp4", "kapak_video9_waves.png", "How does the sound of a guitar reach your ear with only air in between? 🎸",
        "Ray explains how waves work: they carry energy, not matter. Sound is a pressure wave, and speed = frequency × wavelength. Save this for later.",
        ["#waves", "#soundwaves", "#learnphysics"],
        "If you could see sound waves, what sound would you look at first? 👇"),
    10: ("video10_doppler.mp4", "kapak_video10_doppler.png", "Why does an ambulance siren sound high coming toward you and low going away? 🚑",
         "Ray explains the Doppler effect: motion squeezes and stretches waves, so the pitch changes. It works for light too. Send this to a friend who loves cars.",
         ["#dopplereffect", "#soundwaves", "#sciencefacts"],
         "Where have you noticed this? Sirens, race cars, trains? 👇"),
    11: ("video11_light_sound.mp4", "kapak_video11_light_sound.png", "Why do you see lightning first and only hear thunder seconds later? ⚡",
         "Ray compares the speed of light and the speed of sound, and shows how to count the distance to a storm. Send this to someone who hates thunderstorms.",
         ["#speedoflight", "#thunderstorm", "#learnphysics"],
         "Next storm: count the seconds between flash and thunder, then tell us your number 👇"),
    12: ("video12_reflection.mp4", "kapak_video12_reflection.png", "Why can you see yourself in a mirror but not in a sheet of paper? 🪞",
         "Ray explains the law of reflection: the angle in equals the angle out. Smooth surfaces make images, rough ones scatter light.",
         ["#reflection", "#lightphysics", "#stemeducation"],
         "Which surface at home is the best mirror that isn't a mirror? 👇"),
    13: ("video13_refraction.mp4", "kapak_video13_refraction.png", "Why does a straw look broken in a glass of water? 🥤",
         "Ray explains refraction: light changes speed between materials, so it bends. Try this at home with a glass of water and tell us what you see.",
         ["#refraction", "#lightphysics", "#sciencefacts"],
         "Try it right now with a glass and a pencil. Does yours look broken too? 👇"),
    14: ("video14_rainbow.mp4", "kapak_video14_rainbow.png", "How can plain white sunlight turn into a rainbow? 🌈",
         "Ray shows dispersion: white light is a mix of colors, and each color bends by a different amount. Send this to someone who chases rainbows.",
         ["#rainbow", "#dispersion", "#learnphysics"],
         "Which color of the rainbow bends the most? Answer before you scroll up 👇"),
    15: ("video15_static.mp4", "kapak_video15_static.png", "Why does a balloon stick to the wall after you rub it on your hair? 🎈",
         "Ray explains static electricity and electric charge: rubbing moves electrons, opposite charges attract. Save this and try it with a balloon.",
         ["#staticelectricity", "#electriccharge", "#sciencefacts"],
         "Have you ever shocked yourself on a doorknob? Tell us your best story ⚡👇"),
    16: ("video16_magnetism.mp4", "kapak_video16_magnetism.png", "Why do two magnets snap together without even touching? 🧲",
         "Ray explains magnetism, poles and magnetic fields, and how a current in a coil makes an electromagnet. Send this to a friend with fridge magnets.",
         ["#magnetism", "#magneticfield", "#stemeducation"],
         "What happens if you cut a magnet in half? Guess first 👇"),
    17: ("video17_gravity.mp4", "kapak_video17_gravity.png", "If gravity pulls everything down, why doesn't the Moon crash into Earth? 🌙",
         "Ray explains gravity and orbits: an orbit is falling while moving sideways fast enough to miss the ground. Send this to a space fan.",
         ["#gravity", "#orbit", "#learnphysics"],
         "Are astronauts really weightless? Give us your answer, then watch the end 👇"),
    18: ("video18_circular_motion.mp4", "kapak_video18_circular_motion.png", "Why do you feel pushed against the door when a car takes a sharp turn? 🚗",
         "Ray explains circular motion, centripetal force and inertia. The outward push you feel isn't a force. Send this to a friend who drives fast.",
         ["#centripetalforce", "#circularmotion", "#sciencefacts"],
         "Double the speed in a turn: how much more force do you need? 👇"),
    19: ("video19_buoyancy.mp4", "kapak_video19_buoyancy.png", "How can a giant steel ship float when a tiny steel nail sinks? 🚢",
         "Ray explains pressure, buoyant force and Archimedes' principle: floating depends on average density. Save this for later.",
         ["#archimedes", "#buoyancy", "#learnphysics"],
         "Would a steel ship float if it were a solid block? Tell us why 👇"),
    20: ("video20_friction.mp4", "kapak_video20_friction.png", "Why is ice so slippery and sandpaper so grippy? 🧊",
         "Ray explains friction: rough surfaces, the friction coefficient and why static friction beats sliding friction. Send this to someone who just fell on ice.",
         ["#friction", "#forceandmotion", "#stemeducation"],
         "Where is friction your best friend, and where is it your enemy? 👇"),
    21: ("video21_momentum.mp4", "kapak_video21_momentum.png", "Why is a slow truck harder to stop than a fast bicycle? 🚚",
         "Ray explains momentum and impulse: p = m·v, and why airbags work by making a stop last longer. Save this for your next physics exam.",
         ["#momentum", "#impulse", "#sciencefacts"],
         "Would you rather be hit by a bowling ball at 1 m/s or a baseball at 40 m/s? Explain with momentum 👇"),
    22: ("video22_levers.mp4", "kapak_video22_levers.png", "How can a small push lift a heavy rock? 🪨",
         "Ray explains levers, the fulcrum and torque: a longer arm means less force, but you push farther. Send this to someone who loves tools.",
         ["#levers", "#torque", "#learnphysics"],
         "Which lever do you use every day without noticing? 👇"),
    23: ("video23_relativity.mp4", "kapak_video23_relativity.png", "Does time really slow down when you move fast? ⏱️",
         "Ray explains Einstein's relativity and time dilation with a light clock, and why GPS needs relativity to work. Send this to the friend who loves space.",
         ["#relativity", "#einstein", "#stemeducation"],
         "Does it blow your mind that GPS needs relativity? Tell us what you think 👇"),
}

# Hedef kitle ABD/Kanada/İngiltere. 12:30 UTC = 13:30 UK / 08:30 ET / 05:30 PT; 17:00 UTC = 18:00 UK / 13:00 ET / 10:00 PT; 21:00 UTC = 22:00 UK / 17:00 ET / 14:00 PT (22 Ekim haftası, yaz saati)
SLOTS_UTC = ["12:30", "17:00", "21:00"]
FIRST_DAY = dt.date(2026, 10, 17)
FIRST_NO = 4      # 3. video 17 Ekim 12:25 UTC'de otopilot ile paylaşıldı; plan bugünün 16:30 slotundan başlar
SKIP_SLOTS = 1    # bugünün 12:30 slotu (video 3) kullanıldı


def plan():
    rows = []
    for i, no in enumerate(n for n in sorted(COPY) if n >= FIRST_NO):
        j = i + SKIP_SLOTS
        day = FIRST_DAY + dt.timedelta(days=j // 3)
        h, m = map(int, SLOTS_UTC[j % 3].split(":"))
        t = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=dt.timezone.utc)
        rows.append((no, t))
    return rows


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    qf = os.path.join(ROOT, "queue", "queue.json")
    if cmd == "patch":
        q = json.load(open(qf, encoding="utf8"))
        for it in q:
            no = int(it["id"].split("_video")[1].split("_")[0])
            if no in COPY:
                _, _, hook, body, tags, fc = COPY[no]
                it.update(hook=hook, body=body, tags=tags, first_comment=fc)
        json.dump(q, open(qf, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print("güncellendi:", len(q))
    elif cmd == "enqueue":
        for no in sorted(COPY):
            if no < 9:
                continue  # 3-8 zaten kuyrukta (patch ile güncellenir)
            vid, cov, hook, body, tags, fc = COPY[no]
            subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "enqueue.py"), "--video", os.path.join(V, vid),
                                   "--cover", os.path.join(K, cov), "--hook", hook, "--body", body,
                                   "--tags", " ".join(tags), "--first-comment", fc])
    else:
        for no, t in plan():
            tr = t + dt.timedelta(hours=3)
            et = t - dt.timedelta(hours=4)
            print(f"video {no:>2} | UTC {t:%Y-%m-%d %H:%M} | TR {tr:%d.%m %H:%M} | ET {et:%a %H:%M}")


if __name__ == "__main__":
    main()
