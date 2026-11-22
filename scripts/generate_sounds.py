#!/usr/bin/env python
"""
Generate placeholder sound effects for Aether Strife: Origins
Uses numpy to create simple synthesized audio
"""

import numpy as np
import wave
import os
import struct

SAMPLE_RATE = 44100
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sounds')

def generate_tone(freq, duration, volume=0.3, fade_out=True, envelope='linear'):
    """Generate a simple tone with optional envelope"""
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)
    
    # Generate base wave
    wave_data = np.sin(2 * np.pi * freq * t) * volume
    
    # Apply envelope
    if envelope == 'linear':
        env = np.linspace(1, 0, samples) if fade_out else np.ones(samples)
    elif envelope == 'exponential':
        env = np.exp(-3 * t / duration)
    else:
        env = np.ones(samples)
    
    wave_data = wave_data * env
    return (wave_data * 32767).astype(np.int16)

def generate_noise(duration, volume=0.2):
    """Generate white noise"""
    samples = int(SAMPLE_RATE * duration)
    noise = np.random.uniform(-1, 1, samples) * volume
    return (noise * 32767).astype(np.int16)

def save_wav(filename, data):
    """Save audio data as WAV file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data.tobytes())
    print(f"  Generated: {filename}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("🔊 Generating sound effects...")
    
    # Attack sound - short percussive hit
    attack = np.concatenate([
        generate_tone(200, 0.05, 0.4, envelope='exponential'),
        generate_noise(0.08, 0.3)
    ])
    save_wav('attack.wav', attack)
    
    # Ability sound - magical whoosh
    ability = np.concatenate([
        generate_tone(400, 0.1, 0.3, envelope='exponential'),
        generate_tone(600, 0.1, 0.25, envelope='exponential'),
        generate_noise(0.15, 0.2)
    ])
    save_wav('ability.wav', ability)
    
    # Kill sound - triumphant chord
    kill = np.concatenate([
        generate_tone(523, 0.15, 0.3, envelope='exponential'),  # C5
        generate_tone(659, 0.15, 0.25, envelope='exponential'), # E5
        generate_tone(784, 0.2, 0.2, envelope='exponential'),   # G5
    ])
    save_wav('kill.wav', kill)
    
    # Purchase sound - coin clink
    purchase = np.concatenate([
        generate_tone(1200, 0.05, 0.3, envelope='exponential'),
        generate_tone(1800, 0.08, 0.25, envelope='exponential'),
    ])
    save_wav('purchase.wav', purchase)
    
    # Level up sound - ascending arpeggio
    levelup = np.concatenate([
        generate_tone(523, 0.1, 0.3, envelope='exponential'),
        generate_tone(659, 0.1, 0.3, envelope='exponential'),
        generate_tone(784, 0.1, 0.3, envelope='exponential'),
        generate_tone(1047, 0.2, 0.3, envelope='exponential'),
    ])
    save_wav('levelup.wav', levelup)
    
    # Upgrade sound - powerful chime
    upgrade = np.concatenate([
        generate_tone(880, 0.1, 0.3, envelope='exponential'),
        generate_tone(1175, 0.15, 0.3, envelope='exponential'),
        generate_tone(1760, 0.2, 0.25, envelope='exponential'),
    ])
    save_wav('upgrade.wav', upgrade)
    
    print("✅ Sound generation complete!")

if __name__ == '__main__':
    main()
