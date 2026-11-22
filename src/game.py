#!/usr/bin/env python
"""
AETHER STRIFE: ORIGINS - v9.0
A complete 2D Pre-MOBA game built with Pygame

Features:
- 5 unique heroes with passives and abilities
- Ability upgrade system at levels 6, 10, 13
- 3 lanes with proper minion pathing
- Towers, Nexuses, Jungle camps
- Drake & Titan neutral objectives with buffs
- Fog of War with wards
- Item shop with 9 items (buy & sell)
- Leveling system (1-16)
- Respawn timers
- CC effects (Stun/Slow/Root)
- Recall to base
- Match timer, Kill feed, GPM tracking
- Gold bounties on killing sprees
- Assist tracking and gold sharing
- Enhanced enemy AI
- Pause menu, Settings menu, Minimap
- Game modes (Standard/Duel)
- Right-click movement / Left-click attack
"""

import pygame
import sys
import math
import random
import os

# --- CONSTANTS & SETUP ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 700
MAP_WIDTH, MAP_HEIGHT = 3600, 1400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aether Strife: Origins - v9.0")
clock = pygame.time.Clock()

# Colors
BG_COLOR = (20, 20, 30)
LANE_COLOR = (40, 40, 55)
JUNGLE_COLOR = (25, 50, 30)
BLUE_TEAM = (50, 100, 255)
RED_TEAM = (255, 60, 60)
GOLD_COLOR = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
MANA_BLUE = (50, 150, 255)
PURPLE = (180, 80, 220)
FOG_COLOR = (0, 0, 0, 210)
MINIMAP_BG = (10, 10, 15)
WARD_COLOR = (255, 255, 100, 80)
DRAKE_COLOR = (100, 200, 255)
TITAN_COLOR = (200, 50, 50)
STUN_COLOR = (255, 255, 0)
SLOW_COLOR = (100, 150, 255)
ROOT_COLOR = (150, 100, 50)
PASSIVE_COLOR = (255, 150, 200)
BOUNTY_COLOR = (255, 100, 0)
ASSIST_COLOR = (150, 255, 150)

# Game Settings
MINION_SPAWN_TIME = 3000
MINION_SPEED = 1.5
TOWER_RANGE = 250
RESPAWN_TIME = 8000
MAX_LEVEL = 16
WARD_DURATION = 30000
MAX_WARDS = 3
RECALL_TIME = 3000
DRAKE_SPAWN_TIME = 240000
TITAN_SPAWN_TIME = 600000
ASSIST_WINDOW = 10000

# Sound effects
sounds = {}
sounds_available = False

def load_sounds():
    global sounds_available
    sound_files = ['attack', 'ability', 'kill', 'purchase', 'levelup', 'upgrade']
    sound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sounds')
    
    for name in sound_files:
        filepath = os.path.join(sound_dir, f"{name}.wav")
        if os.path.exists(filepath):
            try:
                sounds[name] = pygame.mixer.Sound(filepath)
            except:
                pass
    
    sounds_available = len(sounds) > 0

def play_sound(sound_name):
    if sounds_available and sound_name in sounds:
        sounds[sound_name].set_volume(settings["master_volume"])
        sounds[sound_name].play()

settings = {
    "master_volume": 1.0,
    "smart_cast": True,
    "show_range_indicators": True
}

# --- HELPER FUNCTIONS ---
def get_distance(obj1, obj2):
    return math.hypot(obj1.rect.centerx - obj2.rect.centerx, obj1.rect.centery - obj2.rect.centery)

def draw_bars(surface, entity, camera_x, camera_y):
    bar_width = entity.rect.width
    x = entity.rect.x - camera_x
    y = entity.rect.y - 14
    
    if x < -50 or x > WIDTH + 50 or y < -50 or y > HEIGHT + 50:
        return
    
    hp_color = GREEN
    hp_ratio = max(0, entity.hp / entity.max_hp)
    if hp_ratio < 0.3:
        hp_color = RED_TEAM
    elif hp_ratio < 0.6:
        hp_color = (255, 200, 50)
    
    pygame.draw.rect(surface, BLACK, (x, y, bar_width, 5))
    pygame.draw.rect(surface, hp_color, (x, y, bar_width * hp_ratio, 5))
    
    if hasattr(entity, 'max_mana'):
        pygame.draw.rect(surface, BLACK, (x, y + 6, bar_width, 4))
        mana_ratio = max(0, entity.mana / entity.max_mana)
        pygame.draw.rect(surface, MANA_BLUE, (x, y + 6, bar_width * mana_ratio, 4))

# --- PARTICLE SYSTEM ---
particles = []
def spawn_particles(pos, color, count=10, speed=3, life=30):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, speed)
        particles.append({
            "x": pos[0], "y": pos[1],
            "vx": math.cos(angle) * spd,
            "vy": math.sin(angle) * spd,
            "color": color,
            "life": life,
            "max_life": life
        })

def update_draw_particles(surface, camera_x, camera_y):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        alpha = int(255 * (p["life"] / p["max_life"]))
        color = (*p["color"][:3], alpha)
        try:
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            s.fill(color)
            surface.blit(s, (int(p["x"] - camera_x), int(p["y"] - camera_y)))
        except:
            pass
        if p["life"] <= 0:
            particles.remove(p)

# --- TEXT EFFECTS ---
text_effects = []
def spawn_text_effect(pos, text, color):
    text_effects.append({"pos": list(pos), "text": text, "color": color, "life": 50})

def update_draw_text_effects(surface, camera_x, camera_y):
    font = pygame.font.SysFont("arial", 16, bold=True)
    for effect in text_effects[:]:
        effect["life"] -= 1
        effect["pos"][1] -= 1
        txt_surf = font.render(effect["text"], True, effect["color"])
        surface.blit(txt_surf, (effect["pos"][0] - camera_x, effect["pos"][1] - camera_y))
        if effect["life"] <= 0:
            text_effects.remove(effect)

# --- KILL FEED ---
kill_feed = []
def add_kill_feed(text, color):
    kill_feed.append({"text": text, "color": color, "life": 300})

def update_draw_kill_feed(surface):
    font = pygame.font.SysFont("arial", 14, bold=True)
    y_offset = 40
    for entry in kill_feed[:]:
        entry["life"] -= 1
        txt_surf = font.render(entry["text"], True, entry["color"])
        surface.blit(txt_surf, (WIDTH - txt_surf.get_width() - 10, y_offset))
        y_offset += 20
        if entry["life"] <= 0:
            kill_feed.remove(entry)

# --- SCREEN SHAKE ---
screen_shake = 0
def trigger_screen_shake(intensity=5):
    global screen_shake
    screen_shake = intensity

# --- CLASSES ---
class Entity:
    def __init__(self, x, y, w, h, color, hp, team):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.team = team
        self.alive = True
        self.stun_timer = 0
        self.slow_timer = 0
        self.slow_amount = 0
        self.root_timer = 0
        self.recent_damage = {}

class Hero(Entity):
    def __init__(self, x, y, color, team, hero_type="bruiser", is_player=False):
        super().__init__(x, y, 30, 30, color, 800, team)
        self.is_player = is_player
        self.hero_type = hero_type
        self.gold = 0
        self.last_hits = 0
        self.denies = 0
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.gold_earned_total = 0
        self.kill_streak = 0
        self.bounty = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.upgrades_available = 0
        self.upgrades_chosen = {"q": [], "w": [], "e": [], "r": []}
        
        if hero_type == "bruiser":
            self.base_speed = 4
            self.base_attack_damage = 50
            self.base_max_mana = 120
            self.max_hp = 1000
            self.hp = 1000
            self.passive_desc = "IRON WILL: Every 3rd attack heals"
            self.hero_color = (100, 150, 255)
        elif hero_type == "mage":
            self.base_speed = 3.5
            self.base_attack_damage = 35
            self.base_max_mana = 200
            self.max_hp = 600
            self.hp = 600
            self.passive_desc = "SPELLWEAVE: Abilities boost next attack"
            self.hero_color = (200, 100, 255)
        elif hero_type == "assassin":
            self.base_speed = 5
            self.base_attack_damage = 55
            self.base_max_mana = 100
            self.max_hp = 700
            self.hp = 700
            self.passive_desc = "SHADOW STEP: +20% speed in fog"
            self.hero_color = (255, 100, 100)
        elif hero_type == "support":
            self.base_speed = 4
            self.base_attack_damage = 30
            self.base_max_mana = 180
            self.max_hp = 750
            self.hp = 750
            self.passive_desc = "TALLY: Earn gold on heals"
            self.hero_color = (100, 255, 150)
        elif hero_type == "marksman":
            self.base_speed = 4.2
            self.base_attack_damage = 60
            self.base_max_mana = 80
            self.max_hp = 550
            self.hp = 550
            self.attack_range = 120
            self.passive_desc = "FOCUS: Attacks grant stacking AD"
            self.hero_color = (255, 200, 100)
        
        self.speed = self.base_speed
        self.attack_damage = self.base_attack_damage
        if hero_type != "marksman":
            self.attack_range = 80
        self.attack_cooldown = 0
        self.mana = self.base_max_mana
        self.max_mana = self.base_max_mana
        self.mana_regen = 0.15
        self.q_cd = 0
        self.w_cd = 0
        self.e_cd = 0
        self.r_cd = 0
        self.shield_active = 0
        self.attack_count = 0
        self.passive_bonus_ad = 0
        self.passive_boost = 0
        self.passive_heal_gold = 0
        self.move_target = None
        self.attack_target = None
        self.recalling = False
        self.recall_timer = 0
        self.recall_target = None
        self.drake_buff = 0
        self.titan_buff = 0
        self.respawn_timer = 0
        self.spawn_x = x
        self.spawn_y = y
        self.has_sword = False
        self.has_boots = False
        self.has_mana_crystal = False
        self.has_armor = False
        self.has_lifesteal = False
        self.ward_count = 0
        self.has_magic_resist = False
        self.has_cooldown_reduction = False
        self.potion_count = 0
        self.game_time = 0

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next and self.level < MAX_LEVEL:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.4)
            self.level_up()
            if self.level in [6, 10, 13]:
                self.upgrades_available += 1
                if self.is_player:
                    spawn_text_effect(self.rect.center, "UPGRADE AVAILABLE!", GOLD_COLOR)

    def level_up(self):
        self.max_hp += 80
        self.hp = min(self.hp + 80, self.max_hp)
        self.base_max_mana += 20
        self.max_mana = self.base_max_mana
        self.mana = min(self.mana + 20, self.max_mana)
        self.base_attack_damage += 8
        self.attack_damage = self.base_attack_damage
        if self.has_sword: self.attack_damage += 30
        self.attack_damage += self.passive_bonus_ad
        spawn_text_effect(self.rect.center, f"LEVEL {self.level}!", GOLD_COLOR)
        spawn_particles(self.rect.center, GOLD_COLOR, 20, 4, 40)
        play_sound('levelup')

    def die(self):
        self.alive = False
        self.deaths += 1
        self.respawn_timer = RESPAWN_TIME
        self.recalling = False
        self.recall_timer = 0
        self.kill_streak = 0
        self.bounty = 0
        spawn_particles(self.rect.center, self.color, 30, 5, 50)
        play_sound('kill')
        add_kill_feed(f"{'You' if self.is_player else 'Enemy'} died!", self.color)

    def respawn(self):
        self.alive = True
        self.hp = self.max_hp
        self.mana = self.max_mana
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.shield_active = 0
        self.stun_timer = 0
        self.slow_timer = 0
        self.root_timer = 0
        spawn_text_effect(self.rect.center, "RESPAWNED!", GREEN)
        spawn_particles(self.rect.center, GREEN, 20, 4, 40)

    def apply_cc(self, cc_type, duration, amount=0):
        if cc_type == "stun":
            self.stun_timer = duration
            self.recalling = False
        elif cc_type == "slow":
            self.slow_timer = duration
            self.slow_amount = amount
        elif cc_type == "root":
            self.root_timer = duration
            self.recalling = False

    def start_recall(self, target_x, target_y):
        if not self.alive or self.stun_timer > 0: return
        self.recalling = True
        self.recall_timer = RECALL_TIME
        self.recall_target = (target_x, target_y)
        spawn_text_effect(self.rect.center, "RECALLING...", MANA_BLUE)

    def cancel_recall(self):
        if self.recalling:
            self.recalling = False
            self.recall_timer = 0
            spawn_text_effect(self.rect.center, "CANCELLED", RED_TEAM)

    def update_base(self, mouse_pos=None, camera_x=0, camera_y=0):
        if not self.alive:
            self.respawn_timer -= 16.67
            if self.respawn_timer <= 0:
                self.respawn()
            return
        
        if self.stun_timer > 0: self.stun_timer -= 1
        if self.slow_timer > 0: self.slow_timer -= 1
        if self.root_timer > 0: self.root_timer -= 1
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.q_cd > 0: self.q_cd -= 1
        if self.w_cd > 0: self.w_cd -= 1
        if self.e_cd > 0: self.e_cd -= 1
        if self.r_cd > 0: self.r_cd -= 1
        if self.shield_active > 0: self.shield_active -= 1
        if self.drake_buff > 0: self.drake_buff -= 1
        if self.titan_buff > 0: self.titan_buff -= 1
        
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + self.mana_regen)
        
        self.game_time += 16.67

        if self.recalling:
            self.recall_timer -= 16.67
            if self.recall_timer <= 0:
                self.rect.x = self.recall_target[0]
                self.rect.y = self.recall_target[1]
                self.recalling = False
                self.hp = self.max_hp
                self.mana = self.max_mana
                spawn_text_effect(self.rect.center, "RECALLED!", GREEN)
                spawn_particles(self.rect.center, GREEN, 25, 4, 40)
            return

        if self.is_player and self.stun_timer <= 0 and self.root_timer <= 0:
            if self.move_target:
                dx = self.move_target[0] - self.rect.centerx
                dy = self.move_target[1] - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 5:
                    speed = self.speed
                    if self.slow_timer > 0:
                        speed *= (1 - self.slow_amount)
                    if self.drake_buff > 0:
                        speed *= 1.15
                    self.rect.x += (dx / dist) * speed
                    self.rect.y += (dy / dist) * speed
                else:
                    self.move_target = None
            self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))

    def basic_attack(self, target):
        if self.attack_cooldown > 0 or not self.alive or self.stun_timer > 0: return
        if not target or not target.alive: return
        
        dist = get_distance(self, target)
        if dist > self.attack_range:
            self.attack_target = target
            self.move_target = (target.rect.centerx, target.rect.centery)
            return
        
        damage = self.attack_damage
        if self.hero_type == "mage" and self.passive_boost > 0:
            damage = int(damage * 1.5)
            self.passive_boost = 0
        
        if hasattr(target, 'shield_active') and target.shield_active > 0:
            damage = int(damage * 0.5)
        
        target.hp -= damage
        if hasattr(target, 'recent_damage'):
            target.recent_damage[id(self)] = {"damage": damage, "time": self.game_time}
        
        self.attack_cooldown = 30
        play_sound('attack')
        
        if self.has_lifesteal and isinstance(target, (Minion, JungleCamp, NeutralObjective)):
            heal = int(damage * 0.15)
            self.hp = min(self.max_hp, self.hp + heal)
        
        if self.hero_type == "bruiser":
            self.attack_count += 1
            if self.attack_count >= 3:
                heal = int(self.max_hp * 0.08)
                self.hp = min(self.max_hp, self.hp + heal)
                spawn_text_effect(self.rect.center, f"+{heal}", GREEN)
                self.attack_count = 0
        
        if self.hero_type == "marksman":
            self.passive_bonus_ad = min(30, self.passive_bonus_ad + 1)
            self.attack_damage = self.base_attack_damage + self.passive_bonus_ad
            if self.has_sword: self.attack_damage += 30
        
        self.check_kill(target)
        spawn_text_effect(target.rect.center, f"-{damage}", RED_TEAM)
        self.attack_target = None

    def cast_q(self, targets, projectiles, mouse_pos=None, camera_x=0, camera_y=0):
        if self.q_cd > 0 or self.mana < 30 or not self.alive or self.stun_timer > 0: return
        self.mana -= 30
        cd = 120
        if self.has_cooldown_reduction: cd = int(cd * 0.8)
        self.q_cd = cd
        if self.hero_type == "mage":
            self.passive_boost = 180
        
        if self.hero_type == "bruiser":
            target = None
            min_dist = 150
            for t in targets:
                if not t.alive or t.team == self.team: continue
                dist = get_distance(self, t)
                if dist < min_dist:
                    min_dist = dist
                    target = t
            if target:
                damage = 80
                stun_duration = 60
                if "q_damage" in self.upgrades_chosen["q"]:
                    damage = int(damage * 1.5)
                if "q_stun" in self.upgrades_chosen["q"]:
                    stun_duration = 90
                target.hp -= damage
                if hasattr(target, 'apply_cc'):
                    target.apply_cc("stun", stun_duration)
                spawn_text_effect(target.rect.center, "STUNNED!", STUN_COLOR)
        elif self.hero_type == "mage":
            if mouse_pos and not settings["smart_cast"]:
                dir_x = (mouse_pos[0] + camera_x - self.rect.centerx)
                dir_y = (mouse_pos[1] + camera_y - self.rect.centery)
                dist = math.hypot(dir_x, dir_y)
                if dist > 0:
                    dir_x /= dist
                    dir_y /= dist
                else:
                    dir_x, dir_y = 1, 0
            else:
                dir_x = 1 if self.team == 0 else -1
                dir_y = 0
            damage = 150
            pierce = 1
            if "q_pierce" in self.upgrades_chosen["q"]:
                pierce = 3
            if "q_damage" in self.upgrades_chosen["q"]:
                damage = 200
            projectiles.append(Projectile(self.rect.center, None, damage, self.team, speed=12, is_skillshot=True, radius=10, dir_x=dir_x, dir_y=dir_y, pierce=pierce, source=self))
        elif self.hero_type == "assassin":
            target = None
            min_dist = 400
            for t in targets:
                if not t.alive or t.team == self.team: continue
                dist = get_distance(self, t)
                if dist < min_dist:
                    min_dist = dist
                    target = t
            if target:
                self.rect.centerx = target.rect.centerx - 30
                self.rect.centery = target.rect.centery
                damage = 120
                if "q_damage" in self.upgrades_chosen["q"]:
                    damage = 180
                target.hp -= damage
                spawn_text_effect(target.rect.center, f"-{damage}", RED_TEAM)
        elif self.hero_type == "support":
            healed = False
            heal_amount = 150
            if "q_heal" in self.upgrades_chosen["q"]:
                heal_amount = 200
            for t in targets:
                if t.alive and t.team == self.team and isinstance(t, Hero) and t != self:
                    t.hp = min(t.max_hp, t.hp + heal_amount)
                    spawn_text_effect(t.rect.center, f"+{heal_amount} HP", GREEN)
                    healed = True
                    self.passive_heal_gold += 15
                    if self.passive_heal_gold >= 50:
                        self.gold += 50
                        self.gold_earned_total += 50
                        self.passive_heal_gold = 0
                        spawn_text_effect(self.rect.center, "+50g (TALLY)", GOLD_COLOR)
                    break
            if not healed:
                self.hp = min(self.max_hp, self.hp + 100)
                spawn_text_effect(self.rect.center, "+100 HP", GREEN)
        elif self.hero_type == "marksman":
            if mouse_pos and not settings["smart_cast"]:
                dir_x = (mouse_pos[0] + camera_x - self.rect.centerx)
                dir_y = (mouse_pos[1] + camera_y - self.rect.centery)
                dist = math.hypot(dir_x, dir_y)
                if dist > 0:
                    dir_x /= dist
                    dir_y /= dist
                else:
                    dir_x, dir_y = 1, 0
            else:
                dir_x = 1 if self.team == 0 else -1
                dir_y = 0
            damage = 100
            pierce = 3
            if "q_pierce" in self.upgrades_chosen["q"]:
                pierce = 5
            if "q_damage" in self.upgrades_chosen["q"]:
                damage = 150
            projectiles.append(Projectile(self.rect.center, None, damage, self.team, speed=15, is_skillshot=True, radius=8, dir_x=dir_x, dir_y=dir_y, pierce=pierce, source=self))
        play_sound('ability')

    def cast_w(self, targets, mouse_pos=None, camera_x=0, camera_y=0):
        if self.w_cd > 0 or self.mana < 25 or not self.alive or self.stun_timer > 0: return
        self.mana -= 25
        cd = 240
        if self.has_cooldown_reduction: cd = int(cd * 0.8)
        self.w_cd = cd
        
        if self.hero_type == "bruiser":
            slow_amount = 0.4
            if "w_slow" in self.upgrades_chosen["w"]:
                slow_amount = 0.6
            for t in targets:
                if t.alive and t.team != self.team and get_distance(self, t) < 200:
                    if hasattr(t, 'apply_cc'):
                        t.apply_cc("slow", 120, slow_amount)
            spawn_particles(self.rect.center, SLOW_COLOR, 20, 4, 30)
        elif self.hero_type == "mage":
            dash_dist = 180 if self.team == 0 else -180
            if "w_distance" in self.upgrades_chosen["w"]:
                dash_dist = 250 if self.team == 0 else -250
            self.rect.x += dash_dist
            self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
            spawn_text_effect(self.rect.center, "BLINK!", MANA_BLUE)
        elif self.hero_type == "assassin":
            dash_dist = 250 if self.team == 0 else -250
            if "w_distance" in self.upgrades_chosen["w"]:
                dash_dist = 350 if self.team == 0 else -350
            self.rect.x += dash_dist
            self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
            spawn_text_effect(self.rect.center, "BLINK!", MANA_BLUE)
        elif self.hero_type == "support":
            speed_mult = 1.3
            if "w_speed" in self.upgrades_chosen["w"]:
                speed_mult = 1.5
            self.speed = self.base_speed * speed_mult
            spawn_text_effect(self.rect.center, "SPEED!", GREEN)
        elif self.hero_type == "marksman":
            if mouse_pos:
                trap_x = mouse_pos[0] + camera_x
                trap_y = mouse_pos[1] + camera_y
                root_duration = 90
                if "w_root" in self.upgrades_chosen["w"]:
                    root_duration = 120
                for t in targets:
                    if t.alive and t.team != self.team:
                        if math.hypot(t.rect.centerx - trap_x, t.rect.centery - trap_y) < 100:
                            if hasattr(t, 'apply_cc'):
                                t.apply_cc("root", root_duration)
                            spawn_text_effect(t.rect.center, "ROOTED!", ROOT_COLOR)
        spawn_particles(self.rect.center, MANA_BLUE, 15, 3, 25)
        play_sound('ability')

    def cast_e(self, targets, projectiles):
        if self.e_cd > 0 or self.mana < 40 or not self.alive or self.stun_timer > 0: return
        self.mana -= 40
        cd = 300
        if self.has_cooldown_reduction: cd = int(cd * 0.8)
        self.e_cd = cd
        
        if self.hero_type == "bruiser":
            duration = 180 + self.level * 5
            if "e_duration" in self.upgrades_chosen["e"]:
                duration += 60
            self.shield_active = duration
            spawn_text_effect(self.rect.center, "SHIELD!", MANA_BLUE)
        elif self.hero_type == "mage":
            damage = 100
            if "e_damage" in self.upgrades_chosen["e"]:
                damage = 150
            for t in targets:
                if t.alive and t.team != self.team and get_distance(self, t) < 250:
                    t.hp -= damage
                    spawn_text_effect(t.rect.center, f"-{damage}", RED_TEAM)
            spawn_particles(self.rect.center, PURPLE, 30, 5, 40)
        elif self.hero_type == "assassin":
            self.attack_damage = self.base_attack_damage * 2 + self.passive_bonus_ad
            if self.has_sword: self.attack_damage += 30
            spawn_text_effect(self.rect.center, "BACKSTAB!", RED_TEAM)
        elif self.hero_type == "support":
            push_distance = 100
            if "e_push" in self.upgrades_chosen["e"]:
                push_distance = 150
            for t in targets:
                if t.alive and t.team != self.team and get_distance(self, t) < 200:
                    dx = t.rect.centerx - self.rect.centerx
                    dy = t.rect.centery - self.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        t.rect.x += (dx / dist) * push_distance
                        t.rect.y += (dy / dist) * push_distance
        elif self.hero_type == "marksman":
            dash_dist = -150 if self.team == 0 else 150
            self.rect.x += dash_dist
            self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
            dir_x = 1 if self.team == 0 else -1
            projectiles.append(Projectile(self.rect.center, None, 80, self.team, speed=12, is_skillshot=True, radius=8, dir_x=dir_x, source=self))
        spawn_particles(self.rect.center, MANA_BLUE, 12, 2, 30)
        play_sound('ability')

    def cast_r(self, targets, projectiles, mouse_pos=None, camera_x=0, camera_y=0):
        if self.r_cd > 0 or self.mana < 80 or not self.alive or self.stun_timer > 0: return
        self.mana -= 80
        cd = 600
        if self.has_cooldown_reduction: cd = int(cd * 0.8)
        self.r_cd = cd
        damage = 150 + self.level * 15
        projectile_count = 3
        if "r_damage" in self.upgrades_chosen["r"]:
            damage = int(damage * 1.3)
        if "r_projectiles" in self.upgrades_chosen["r"]:
            projectile_count = 5
        if self.hero_type == "mage":
            projectile_count = 5 if "r_projectiles" not in self.upgrades_chosen["r"] else 7
        for i in range(-(projectile_count // 2), (projectile_count // 2) + 1):
            angle = i * 0.25
            dir_x = math.cos(angle) * (1 if self.team == 0 else -1)
            dir_y = math.sin(angle)
            projectiles.append(Projectile(self.rect.center, None, damage, self.team, speed=14, is_skillshot=True, radius=12, dir_x=dir_x, dir_y=dir_y, source=self))
        spawn_text_effect(self.rect.center, "ULTIMATE!", GOLD_COLOR)
        spawn_particles(self.rect.center, GOLD_COLOR, 25, 5, 40)
        trigger_screen_shake(8)
        play_sound('ability')

    def use_potion(self):
        if self.potion_count > 0 and self.alive:
            self.potion_count -= 1
            heal = 200
            self.hp = min(self.max_hp, self.hp + heal)
            spawn_text_effect(self.rect.center, f"+{heal} HP", GREEN)
            play_sound('purchase')

    def place_ward(self, wards):
        if self.ward_count >= MAX_WARDS or not self.alive: return
        self.ward_count += 1
        wards.append(Ward(self.rect.centerx, self.rect.centery, self.team))
        spawn_text_effect(self.rect.center, "WARD PLACED!", WARD_COLOR[:3])

    def sell_item(self, item_name):
        item_values = {
            "sword": (400, "has_sword"),
            "boots": (300, "has_boots"),
            "mana_crystal": (500, "has_mana_crystal"),
            "armor": (600, "has_armor"),
            "lifesteal": (700, "has_lifesteal"),
            "magic_resist": (500, "has_magic_resist"),
            "cooldown_reduction": (800, "has_cooldown_reduction"),
        }
        if item_name in item_values:
            base_value, attr = item_values[item_name]
            if getattr(self, attr):
                sell_value = base_value // 2
                self.gold += sell_value
                setattr(self, attr, False)
                if item_name == "sword":
                    self.attack_damage -= 30
                    self.base_attack_damage = self.attack_damage - self.passive_bonus_ad
                elif item_name == "boots":
                    self.speed -= 2
                    self.base_speed = self.speed
                elif item_name == "mana_crystal":
                    self.max_mana -= 50
                    self.mana = min(self.mana, self.max_mana)
                    self.base_max_mana = self.max_mana
                elif item_name == "armor":
                    self.max_hp -= 300
                    self.hp = min(self.hp, self.max_hp)
                spawn_text_effect(self.rect.center, f"SOLD +{sell_value}g", GOLD_COLOR)
                play_sound('purchase')
                return True
        return False

    def check_kill(self, target):
        if target.hp <= 0:
            target.alive = False
            if isinstance(target, Hero) and hasattr(target, 'recent_damage'):
                current_time = self.game_time
                for attacker_id, damage_info in target.recent_damage.items():
                    if current_time - damage_info["time"] < ASSIST_WINDOW:
                        if attacker_id != id(self):
                            # Note: In a full game, we'd look up the hero by id
                            pass
            if target.team == self.team and hasattr(target, 'was_low_hp') and target.was_low_hp:
                self.denies += 1
                self.gold += 10
                self.gold_earned_total += 10
                self.gain_xp(20)
                spawn_text_effect(target.rect.center, "DENY!", GOLD_COLOR)
            elif target.team != self.team and isinstance(target, Minion):
                self.last_hits += 1
                self.gold += 50
                self.gold_earned_total += 50
                self.gain_xp(40)
                spawn_text_effect(target.rect.center, "+50g", GOLD_COLOR)
            elif target.team != self.team and isinstance(target, (JungleCamp, NeutralObjective)):
                self.gold += target.gold_reward
                self.gold_earned_total += target.gold_reward
                self.gain_xp(target.xp_reward)
                spawn_text_effect(target.rect.center, f"+{target.gold_reward}g", GOLD_COLOR)
                if isinstance(target, NeutralObjective):
                    if target.obj_type == "drake":
                        self.drake_buff = 6000
                        spawn_text_effect(self.rect.center, "DRAKE BUFF!", DRAKE_COLOR)
                    elif target.obj_type == "titan":
                        self.titan_buff = 9000
                        spawn_text_effect(self.rect.center, "TITAN BUFF!", TITAN_COLOR)
            elif target.team != self.team and isinstance(target, Hero):
                target.die()
                self.kills += 1
                self.kill_streak += 1
                base_gold = 300
                bounty_bonus = 0
                if self.kill_streak >= 3:
                    bounty_bonus = (self.kill_streak - 2) * 100
                    target.bounty = bounty_bonus
                total_gold = base_gold + target.bounty
                self.gold += total_gold
                self.gold_earned_total += total_gold
                self.gain_xp(200)
                spawn_text_effect(target.rect.center, "KILL!", GOLD_COLOR)
                if bounty_bonus > 0:
                    spawn_text_effect(target.rect.center, f"+{bounty_bonus}g BOUNTY!", BOUNTY_COLOR)
                spawn_particles(target.rect.center, target.color, 40, 6, 60)
                add_kill_feed(f"{'You' if self.is_player else 'Enemy'} killed {'you' if target.is_player else 'enemy'}!", self.color)
            elif target.team != self.team and isinstance(target, Nexus):
                spawn_text_effect(target.rect.center, "NEXUS DESTROYED!", GOLD_COLOR)
                spawn_particles(target.rect.center, target.color, 60, 8, 80)
                add_kill_feed("NEXUS DESTROYED!", GOLD_COLOR)

class Ward(Entity):
    def __init__(self, x, y, team):
        super().__init__(x - 10, y - 10, 20, 20, WARD_COLOR[:3], 1, team)
        self.duration = WARD_DURATION
        self.vision_range = 200
    def update(self):
        self.duration -= 16.67
        if self.duration <= 0:
            self.alive = False

class Minion(Entity):
    def __init__(self, x, y, team, lane="mid"):
        color = BLUE_TEAM if team == 0 else RED_TEAM
        super().__init__(x, y, 20, 20, color, 120, team)
        self.speed = MINION_SPEED
        self.attack_cooldown = 0
        self.was_low_hp = False
        self.lane = lane
        if lane == "top":
            self.lane_y = 150
        elif lane == "bot":
            self.lane_y = MAP_HEIGHT - 250
        else:
            self.lane_y = HEIGHT // 2
    def update(self, enemies):
        if not self.alive: return
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return
        if self.team == 0 and self.hp < (self.max_hp * 0.20):
            self.was_low_hp = True
        target = None
        min_dist = 150
        for e in enemies:
            if not e.alive: continue
            dist = get_distance(self, e)
            if dist < min_dist:
                min_dist = dist
                target = e
        if target:
            if self.attack_cooldown <= 0:
                damage = 15
                if hasattr(target, 'shield_active') and target.shield_active > 0:
                    damage = int(damage * 0.5)
                target.hp -= damage
                if hasattr(target, 'recent_damage'):
                    target.recent_damage[id(self)] = {"damage": damage, "time": 0}
                self.attack_cooldown = 60
                if target.hp <= 0: target.alive = False
        else:
            speed = self.speed
            if self.slow_timer > 0:
                speed *= (1 - self.slow_amount)
            if self.root_timer <= 0:
                dy = self.lane_y - self.rect.centery
                if abs(dy) > 5:
                    self.rect.y += max(-speed, min(speed, dy))
                else:
                    if self.team == 0: self.rect.x += speed
                    else: self.rect.x -= speed
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.slow_timer > 0: self.slow_timer -= 1
        if self.root_timer > 0: self.root_timer -= 1

class Tower(Entity):
    def __init__(self, x, y, team):
        color = BLUE_TEAM if team == 0 else RED_TEAM
        super().__init__(x, y, 60, 100, color, 3000, team)
        self.attack_cooldown = 0
    def update(self, enemies, projectiles):
        if not self.alive or self.attack_cooldown > 0:
            if self.attack_cooldown > 0: self.attack_cooldown -= 1
            return
        target = None
        min_dist = TOWER_RANGE
        for e in enemies:
            if not e.alive or not isinstance(e, Minion): continue
            dist = get_distance(self, e)
            if dist < min_dist:
                min_dist = dist
                target = e
        if not target:
            for e in enemies:
                if not e.alive or not isinstance(e, Hero): continue
                dist = get_distance(self, e)
                if dist < TOWER_RANGE:
                    target = e
                    break
        if target:
            projectiles.append(Projectile(self.rect.center, target, 100, self.team, speed=10))
            self.attack_cooldown = 60

class Nexus(Entity):
    def __init__(self, x, y, team):
        color = BLUE_TEAM if team == 0 else RED_TEAM
        super().__init__(x, y, 80, 120, color, 4000, team)
        self.is_nexus = True

class JungleCamp(Entity):
    def __init__(self, x, y, team_side, buff_type=None):
        color = PURPLE
        super().__init__(x, y, 40, 40, color, 500, 2)
        self.team_side = team_side
        self.buff_type = buff_type
        self.gold_reward = 80
        self.xp_reward = 60
        self.respawn_timer = 0
        self.initial_x = x
        self.initial_y = y
    def update(self):
        if not self.alive:
            self.respawn_timer -= 16.67
            if self.respawn_timer <= 0:
                self.alive = True
                self.hp = self.max_hp
                self.rect.x = self.initial_x
                self.rect.y = self.initial_y

class NeutralObjective(Entity):
    def __init__(self, x, y, obj_type):
        self.obj_type = obj_type
        if obj_type == "drake":
            color = DRAKE_COLOR
            hp = 1500
            self.gold_reward = 150
            self.xp_reward = 100
        else:
            color = TITAN_COLOR
            hp = 3000
            self.gold_reward = 300
            self.xp_reward = 200
        super().__init__(x, y, 60, 60, color, hp, 2)
        self.active = False
        self.respawn_timer = 0
        self.initial_x = x
        self.initial_y = y
        self.spawn_time = DRAKE_SPAWN_TIME if obj_type == "drake" else TITAN_SPAWN_TIME
        self.game_time = 0
    def update(self):
        self.game_time += 16.67
        if not self.alive:
            self.respawn_timer -= 16.67
            if self.respawn_timer <= 0:
                self.alive = True
                self.hp = self.max_hp
                self.rect.x = self.initial_x
                self.rect.y = self.initial_y
        elif not self.active:
            if self.game_time >= self.spawn_time:
                self.active = True
                add_kill_feed(f"{self.obj_type.upper()} HAS SPAWNED!", self.color)

class Projectile:
    def __init__(self, start_pos, target, damage, team, speed=8, is_skillshot=False, radius=5, dir_x=0, dir_y=0, pierce=1, source=None):
        self.x, self.y = float(start_pos[0]), float(start_pos[1])
        self.target = target
        self.damage = damage
        self.team = team
        self.speed = speed
        self.alive = True
        self.is_skillshot = is_skillshot
        self.radius = radius
        self.dir_x = dir_x if dir_x != 0 else (1 if team == 0 else -1)
        self.dir_y = dir_y
        self.color = GOLD_COLOR if is_skillshot else ((255, 255, 100) if team == 0 else (255, 100, 100))
        self.pierce = pierce
        self.hit_entities = set()
        self.source = source
    def update(self, all_entities):
        if self.is_skillshot:
            self.x += self.speed * self.dir_x
            self.y += self.speed * self.dir_y
            for e in all_entities:
                if not e.alive or e.team == self.team or id(e) in self.hit_entities: continue
                if math.hypot(e.rect.centerx - self.x, e.rect.centery - self.y) < self.radius + 15:
                    damage = self.damage
                    if hasattr(e, 'shield_active') and e.shield_active > 0:
                        damage = int(damage * 0.5)
                    e.hp -= damage
                    if hasattr(e, 'recent_damage') and self.source:
                        e.recent_damage[id(self.source)] = {"damage": damage, "time": self.source.game_time}
                    spawn_text_effect(e.rect.center, f"-{damage}", RED_TEAM)
                    self.hit_entities.add(id(e))
                    if e.hp <= 0:
                        e.alive = False
                        if self.source and hasattr(self.source, 'check_kill'):
                            self.source.check_kill(e)
                    self.pierce -= 1
                    if self.pierce < 0:
                        self.alive = False
                    break
        else:
            if not self.target or not self.target.alive:
                self.alive = False
                return
            dx = self.target.rect.centerx - self.x
            dy = self.target.rect.centery - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                damage = self.damage
                if hasattr(self.target, 'shield_active') and self.target.shield_active > 0:
                    damage = int(damage * 0.5)
                self.target.hp -= damage
                if hasattr(self.target, 'recent_damage') and self.source:
                    self.target.recent_damage[id(self.source)] = {"damage": damage, "time": self.source.game_time}
                spawn_text_effect(self.target.rect.center, f"-{damage}", RED_TEAM)
                self.alive = False
                if self.target.hp <= 0:
                    self.target.alive = False
                    if self.source and hasattr(self.source, 'check_kill'):
                        self.source.check_kill(self.target)
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        if self.x < 0 or self.x > MAP_WIDTH or self.y < 0 or self.y > MAP_HEIGHT:
            self.alive = False

# --- FOG OF WAR ---
fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
def draw_fog(surface, player, blue_minions, wards, camera_x, camera_y):
    fog_surface.fill((0, 0, 0, 0))
    fog_surface.fill(FOG_COLOR)
    if player.alive:
        player_screen_x = player.rect.centerx - camera_x
        player_screen_y = player.rect.centery - camera_y
        pygame.draw.circle(fog_surface, (0, 0, 0, 0), (player_screen_x, player_screen_y), 220)
    for m in blue_minions:
        if m.alive:
            m_screen_x = m.rect.centerx - camera_x
            m_screen_y = m.rect.centery - camera_y
            pygame.draw.circle(fog_surface, (0, 0, 0, 0), (m_screen_x, m_screen_y), 110)
    for w in wards:
        if w.alive and w.team == 0:
            w_screen_x = w.rect.centerx - camera_x
            w_screen_y = w.rect.centery - camera_y
            pygame.draw.circle(fog_surface, (0, 0, 0, 0), (w_screen_x, w_screen_y), w.vision_range)
    surface.blit(fog_surface, (0, 0))

# --- UPGRADE SELECTION UI ---
def get_upgrade_options(ability_name, hero_type):
    upgrades = {
        "bruiser": {
            "q": [("q_damage", "+50% damage"), ("q_stun", "+0.5s stun")],
            "w": [("w_slow", "+20% slow"), ("w_distance", "+40% distance")],
            "e": [("e_duration", "+1s shield")],
        },
        "mage": {
            "q": [("q_damage", "+50% damage"), ("q_pierce", "+2 pierce")],
            "w": [("w_distance", "+40% distance")],
            "e": [("e_damage", "+50 damage")],
        },
        "assassin": {
            "q": [("q_damage", "+50% damage")],
            "w": [("w_distance", "+40% distance")],
            "e": [],
        },
        "support": {
            "q": [("q_heal", "+50 heal")],
            "w": [("w_speed", "+20% speed")],
            "e": [("e_push", "+50 push")],
        },
        "marksman": {
            "q": [("q_damage", "+50% damage"), ("q_pierce", "+2 pierce")],
            "w": [("w_root", "+0.5s root")],
            "e": [],
        },
    }
    return upgrades.get(hero_type, {}).get(ability_name, [])

def upgrade_selection_ui(player):
    selecting = True
    while selecting and player.upgrades_available > 0:
        screen.fill(BG_COLOR)
        title_font = pygame.font.SysFont("arial", 50, bold=True)
        title = title_font.render("CHOOSE ABILITY UPGRADE", True, GOLD_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        font = pygame.font.SysFont("arial", 16)
        small_font = pygame.font.SysFont("arial", 14)
        abilities = [("Q", "q"), ("W", "w"), ("E", "e")]
        y_offset = 150
        all_options = []
        for ability_key, ability_name in abilities:
            upgrades = get_upgrade_options(ability_name, player.hero_type)
            available = [(uid, desc) for uid, desc in upgrades if uid not in player.upgrades_chosen[ability_name]]
            screen.blit(font.render(f"[{ability_key}] - {ability_name.upper()}", True, WHITE), (100, y_offset))
            for i, (upgrade_id, desc) in enumerate(available):
                option_text = f"  [{len(all_options)+1}] {desc}"
                screen.blit(small_font.render(option_text, True, GOLD_COLOR), (150, y_offset + 30 + i * 25))
                all_options.append((ability_name, upgrade_id))
            y_offset += 120
        screen.blit(font.render("Press number to choose upgrade", True, WHITE), (WIDTH//2 - 150, HEIGHT - 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.unicode.isdigit():
                    idx = int(event.unicode) - 1
                    if 0 <= idx < len(all_options):
                        ability_name, upgrade_id = all_options[idx]
                        player.upgrades_chosen[ability_name].append(upgrade_id)
                        player.upgrades_available -= 1
                        spawn_text_effect(player.rect.center, "UPGRADED!", GOLD_COLOR)
                        play_sound('upgrade')
                        selecting = False
        clock.tick(60)

# --- SETTINGS MENU ---
def settings_menu():
    in_settings = True
    while in_settings:
        screen.fill(BG_COLOR)
        title_font = pygame.font.SysFont("arial", 50, bold=True)
        title = title_font.render("SETTINGS", True, GOLD_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        font = pygame.font.SysFont("arial", 20)
        vol_text = f"Master Volume: {int(settings['master_volume'] * 100)}%"
        screen.blit(font.render(vol_text, True, WHITE), (WIDTH//2 - 150, 150))
        screen.blit(font.render("[Up/Down] Adjust", True, GOLD_COLOR), (WIDTH//2 - 150, 180))
        sc_text = f"Smart Cast: {'ON' if settings['smart_cast'] else 'OFF'}"
        screen.blit(font.render(sc_text, True, WHITE), (WIDTH//2 - 150, 250))
        screen.blit(font.render("[S] Toggle", True, GOLD_COLOR), (WIDTH//2 - 150, 280))
        ri_text = f"Show Range Indicators: {'ON' if settings['show_range_indicators'] else 'OFF'}"
        screen.blit(font.render(ri_text, True, WHITE), (WIDTH//2 - 150, 350))
        screen.blit(font.render("[R] Toggle", True, GOLD_COLOR), (WIDTH//2 - 150, 380))
        exit_text = font.render("Press [ESC] to return", True, GOLD_COLOR)
        screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT - 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_settings = False
                elif event.key == pygame.K_UP:
                    settings["master_volume"] = min(1.0, settings["master_volume"] + 0.1)
                elif event.key == pygame.K_DOWN:
                    settings["master_volume"] = max(0.0, settings["master_volume"] - 0.1)
                elif event.key == pygame.K_s:
                    settings["smart_cast"] = not settings["smart_cast"]
                elif event.key == pygame.K_r:
                    settings["show_range_indicators"] = not settings["show_range_indicators"]
        clock.tick(60)

# --- PAUSE MENU ---
def pause_menu():
    paused = True
    while paused:
        screen.fill(BG_COLOR)
        title_font = pygame.font.SysFont("arial", 60, bold=True)
        title = title_font.render("PAUSED", True, GOLD_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        font = pygame.font.SysFont("arial", 24)
        options = [("[ESC] Resume", WHITE), ("[S] Settings", GOLD_COLOR), ("[Q] Quit to Menu", RED_TEAM)]
        for i, (text, color) in enumerate(options):
            txt = font.render(text, True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 300 + i * 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                elif event.key == pygame.K_s:
                    settings_menu()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(60)

# --- GAME MODE SELECTION ---
def game_mode_selection():
    selecting = True
    mode = "standard"
    while selecting:
        screen.fill(BG_COLOR)
        title_font = pygame.font.SysFont("arial", 60, bold=True)
        title = title_font.render("SELECT GAME MODE", True, GOLD_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        modes = [
            {"type": "standard", "name": "STANDARD MATCH", "desc": "3 Lanes, Full Game", "color": BLUE_TEAM},
            {"type": "duel", "name": "LAST HIT DUEL", "desc": "1v1 Practice Mode", "color": RED_TEAM}
        ]
        for i, mode_info in enumerate(modes):
            x = WIDTH//2 - 300 + i * 350
            y = 250
            pygame.draw.rect(screen, mode_info["color"], (x, y, 250, 200))
            pygame.draw.rect(screen, WHITE, (x, y, 250, 200), 3)
            name_font = pygame.font.SysFont("arial", 24, bold=True)
            name = name_font.render(mode_info["name"], True, WHITE)
            screen.blit(name, (x + 125 - name.get_width()//2, y + 30))
            desc_font = pygame.font.SysFont("arial", 16)
            desc = desc_font.render(mode_info["desc"], True, WHITE)
            screen.blit(desc, (x + 125 - desc.get_width()//2, y + 100))
            num_font = pygame.font.SysFont("arial", 20, bold=True)
            num = num_font.render(f"Press [{i+1}]", True, GOLD_COLOR)
            screen.blit(num, (x + 125 - num.get_width()//2, y + 160))
        inst_font = pygame.font.SysFont("arial", 18)
        inst = inst_font.render("Press 1 or 2 to select mode | [S] Settings", True, WHITE)
        screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "standard"
                    selecting = False
                elif event.key == pygame.K_2:
                    mode = "duel"
                    selecting = False
                elif event.key == pygame.K_s:
                    settings_menu()
        clock.tick(60)
    return mode

# --- HERO SELECTION ---
def hero_selection_screen():
    selected_hero = None
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        title_font = pygame.font.SysFont("arial", 60, bold=True)
        title = title_font.render("CHOOSE YOUR HERO", True, GOLD_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        heroes = [
            {"type": "bruiser", "name": "BRUISER", "desc": "Tanky, CC, Shield", "color": (100, 150, 255), "passive": "Iron Will"},
            {"type": "mage", "name": "MAGE", "desc": "Burst, AoE, Skillshots", "color": (200, 100, 255), "passive": "Spellweave"},
            {"type": "assassin", "name": "ASSASSIN", "desc": "Dash, Burst, Mobile", "color": (255, 100, 100), "passive": "Shadow Step"},
            {"type": "support", "name": "SUPPORT", "desc": "Heal, Speed, Utility", "color": (100, 255, 150), "passive": "Tally"},
            {"type": "marksman", "name": "MARKSMAN", "desc": "Range, DPS, Traps", "color": (255, 200, 100), "passive": "Focus"},
        ]
        for i, hero in enumerate(heroes):
            x = WIDTH//2 - 500 + i * 220
            y = 200
            pygame.draw.rect(screen, hero["color"], (x, y, 180, 300))
            pygame.draw.rect(screen, WHITE, (x, y, 180, 300), 3)
            name_font = pygame.font.SysFont("arial", 22, bold=True)
            name = name_font.render(hero["name"], True, WHITE)
            screen.blit(name, (x + 90 - name.get_width()//2, y + 20))
            pygame.draw.circle(screen, WHITE, (x + 90, y + 120), 35)
            desc_font = pygame.font.SysFont("arial", 14)
            desc = desc_font.render(hero["desc"], True, WHITE)
            screen.blit(desc, (x + 90 - desc.get_width()//2, y + 200))
            passive_font = pygame.font.SysFont("arial", 12, bold=True)
            passive = passive_font.render(f"Passive: {hero['passive']}", True, PASSIVE_COLOR)
            screen.blit(passive, (x + 90 - passive.get_width()//2, y + 230))
            num_font = pygame.font.SysFont("arial", 18, bold=True)
            num = num_font.render(f"Press [{i+1}]", True, GOLD_COLOR)
            screen.blit(num, (x + 90 - num.get_width()//2, y + 260))
        inst_font = pygame.font.SysFont("arial", 18)
        inst = inst_font.render("Press 1-5 to select your hero | [S] Settings", True, WHITE)
        screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_hero = "bruiser"
                    selecting = False
                elif event.key == pygame.K_2:
                    selected_hero = "mage"
                    selecting = False
                elif event.key == pygame.K_3:
                    selected_hero = "assassin"
                    selecting = False
                elif event.key == pygame.K_4:
                    selected_hero = "support"
                    selecting = False
                elif event.key == pygame.K_5:
                    selected_hero = "marksman"
                    selecting = False
                elif event.key == pygame.K_s:
                    settings_menu()
        clock.tick(60)
    return selected_hero

# --- MINIMAP ---
def draw_minimap(surface, player, enemy_hero, blue_minions, red_minions, towers, nexuses, jungle_camps, wards, objectives):
    mm_w, mm_h = 200, 100
    mm_x, mm_y = WIDTH - mm_w - 10, HEIGHT - mm_h - 10
    scale_x = mm_w / MAP_WIDTH
    scale_y = mm_h / MAP_HEIGHT
    pygame.draw.rect(surface, MINIMAP_BG, (mm_x, mm_y, mm_w, mm_h))
    pygame.draw.rect(surface, WHITE, (mm_x, mm_y, mm_w, mm_h), 1)
    pygame.draw.rect(surface, LANE_COLOR, (mm_x, mm_y + 10, mm_w, 8))
    pygame.draw.rect(surface, LANE_COLOR, (mm_x, mm_y + mm_h//2 - 4, mm_w, 8))
    pygame.draw.rect(surface, LANE_COLOR, (mm_x, mm_y + mm_h - 18, mm_w, 8))
    for n in nexuses:
        if n.alive:
            pygame.draw.rect(surface, n.color, (mm_x + n.rect.x * scale_x, mm_y + n.rect.y * scale_y, 6, 8))
    for t in towers:
        if t.alive:
            pygame.draw.rect(surface, t.color, (mm_x + t.rect.x * scale_x, mm_y + t.rect.y * scale_y, 4, 6))
    for j in jungle_camps:
        if j.alive:
            pygame.draw.circle(surface, PURPLE, (int(mm_x + j.rect.centerx * scale_x), int(mm_y + j.rect.centery * scale_y)), 2)
    for obj in objectives:
        if obj.alive and obj.active:
            pygame.draw.circle(surface, obj.color, (int(mm_x + obj.rect.centerx * scale_x), int(mm_y + obj.rect.centery * scale_y)), 3)
    for w in wards:
        if w.alive and w.team == 0:
            pygame.draw.circle(surface, WARD_COLOR[:3], (int(mm_x + w.rect.centerx * scale_x), int(mm_y + w.rect.centery * scale_y)), 2)
    for m in blue_minions:
        if m.alive:
            pygame.draw.circle(surface, BLUE_TEAM, (int(mm_x + m.rect.centerx * scale_x), int(mm_y + m.rect.centery * scale_y)), 1)
    for m in red_minions:
        if m.alive:
            pygame.draw.circle(surface, RED_TEAM, (int(mm_x + m.rect.centerx * scale_x), int(mm_y + m.rect.centery * scale_y)), 1)
    if player.alive:
        pygame.draw.circle(surface, WHITE, (int(mm_x + player.rect.centerx * scale_x), int(mm_y + player.rect.centery * scale_y)), 3)
    if enemy_hero.alive:
        pygame.draw.circle(surface, RED_TEAM, (int(mm_x + enemy_hero.rect.centerx * scale_x), int(mm_y + enemy_hero.rect.centery * scale_y)), 3)

# --- MAIN GAME LOOP ---
def main():
    load_sounds()
    game_mode = game_mode_selection()
    hero_type = hero_selection_screen()
    
    spawn_y = HEIGHT // 2 - 15
    if game_mode == "duel":
        player = Hero(200, spawn_y, BLUE_TEAM, 0, hero_type=hero_type, is_player=True)
        enemy_hero = Hero(1000, spawn_y, RED_TEAM, 1, hero_type="bruiser")
    else:
        player = Hero(200, spawn_y, BLUE_TEAM, 0, hero_type=hero_type, is_player=True)
        enemy_hero = Hero(MAP_WIDTH - 250, spawn_y, RED_TEAM, 1, hero_type="bruiser")
    
    blue_minions, red_minions, projectiles, wards = [], [], [], []
    
    if game_mode == "duel":
        towers, nexuses, jungle_camps, objectives = [], [], [], []
    else:
        towers = [
            Tower(100, 150, 0), Tower(MAP_WIDTH - 160, 150, 1),
            Tower(100, HEIGHT//2 - 50, 0), Tower(MAP_WIDTH - 160, HEIGHT//2 - 50, 1),
            Tower(100, MAP_HEIGHT - 250, 0), Tower(MAP_WIDTH - 160, MAP_HEIGHT - 250, 1),
        ]
        nexuses = [Nexus(30, HEIGHT//2 - 60, 0), Nexus(MAP_WIDTH - 110, HEIGHT//2 - 60, 1)]
        jungle_camps = [
            JungleCamp(800, 150, 0, "HASTE"),
            JungleCamp(800, MAP_HEIGHT - 190, 0, "POWER"),
            JungleCamp(MAP_WIDTH - 840, 150, 1, "HASTE"),
            JungleCamp(MAP_WIDTH - 840, MAP_HEIGHT - 190, 1, "POWER"),
        ]
        objectives = [
            NeutralObjective(MAP_WIDTH//2, 250, "drake"),
            NeutralObjective(MAP_WIDTH//2, MAP_HEIGHT - 310, "titan")
        ]

    spawn_timer = 0
    shop_open = False
    running = True
    camera_x = 0
    camera_y = 0
    game_over = False
    victory = False
    attack_move_mode = False
    game_time = 0

    while running:
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        game_time += dt
        
        if player.upgrades_available > 0 and not shop_open and not game_over:
            upgrade_selection_ui(player)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if shop_open:
                        shop_open = False
                    else:
                        pause_menu()
                    continue
                if game_over:
                    if event.key == pygame.K_r:
                        main()
                    continue
                if event.key == pygame.K_b and player.alive:
                    if player.rect.x < 350:
                        shop_open = not shop_open
                    else:
                        player.start_recall(player.spawn_x, player.spawn_y)
                if event.key == pygame.K_v and player.alive and not shop_open:
                    player.place_ward(wards)
                if event.key == pygame.K_f and player.alive and not shop_open:
                    player.use_potion()
                if event.key == pygame.K_a:
                    attack_move_mode = True
                if shop_open and event.key == pygame.K_s:
                    for item in ["cooldown_reduction", "lifesteal", "armor", "mana_crystal", "sword", "boots", "magic_resist"]:
                        if player.sell_item(item):
                            break
                if shop_open:
                    if event.key == pygame.K_1 and player.gold >= 400 and not player.has_sword:
                        player.gold -= 400
                        player.has_sword = True
                        player.attack_damage += 30
                        player.base_attack_damage += 30
                        spawn_text_effect(player.rect.center, "+30 AD!", WHITE)
                        play_sound('purchase')
                    if event.key == pygame.K_2 and player.gold >= 300 and not player.has_boots:
                        player.gold -= 300
                        player.has_boots = True
                        player.speed += 2
                        player.base_speed += 2
                        spawn_text_effect(player.rect.center, "+2 Speed!", WHITE)
                        play_sound('purchase')
                    if event.key == pygame.K_3 and player.gold >= 500 and not player.has_mana_crystal:
                        player.gold -= 500
                        player.has_mana_crystal = True
                        player.max_mana += 50
                        player.mana += 50
                        player.base_max_mana += 50
                        spawn_text_effect(player.rect.center, "+50 Mana!", MANA_BLUE)
                        play_sound('purchase')
                    if event.key == pygame.K_4 and player.gold >= 600 and not player.has_armor:
                        player.gold -= 600
                        player.has_armor = True
                        player.max_hp += 300
                        player.hp += 300
                        spawn_text_effect(player.rect.center, "+300 HP!", GREEN)
                        play_sound('purchase')
                    if event.key == pygame.K_5 and player.gold >= 700 and not player.has_lifesteal:
                        player.gold -= 700
                        player.has_lifesteal = True
                        spawn_text_effect(player.rect.center, "+15% Lifesteal!", RED_TEAM)
                        play_sound('purchase')
                    if event.key == pygame.K_6 and player.gold >= 100:
                        player.gold -= 100
                        player.ward_count += 1
                        spawn_text_effect(player.rect.center, f"Wards: {player.ward_count}/{MAX_WARDS}", WARD_COLOR[:3])
                        play_sound('purchase')
                    if event.key == pygame.K_7 and player.gold >= 500 and not player.has_magic_resist:
                        player.gold -= 500
                        player.has_magic_resist = True
                        spawn_text_effect(player.rect.center, "+20% Magic Resist!", PURPLE)
                        play_sound('purchase')
                    if event.key == pygame.K_8 and player.gold >= 800 and not player.has_cooldown_reduction:
                        player.gold -= 800
                        player.has_cooldown_reduction = True
                        spawn_text_effect(player.rect.center, "-20% Cooldowns!", MANA_BLUE)
                        play_sound('purchase')
                    if event.key == pygame.K_9 and player.gold >= 150:
                        player.gold -= 150
                        player.potion_count += 1
                        spawn_text_effect(player.rect.center, f"Potions: {player.potion_count}", GREEN)
                        play_sound('purchase')
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    attack_move_mode = False
                if event.key == pygame.K_b:
                    if player.recalling:
                        player.cancel_recall()
            if event.type == pygame.MOUSEBUTTONDOWN and not shop_open and not game_over:
                if event.button == 3:
                    player.move_target = (mouse_pos[0] + camera_x, mouse_pos[1] + camera_y)
                    player.attack_target = None
                    if player.recalling:
                        player.cancel_recall()
                elif event.button == 1:
                    if attack_move_mode:
                        all_targets = [m for m in red_minions if m.alive]
                        if enemy_hero.alive: all_targets.append(enemy_hero)
                        if game_mode != "duel":
                            all_targets += [t for t in towers if t.alive]
                            all_targets += [j for j in jungle_camps if j.alive]
                            all_targets += [o for o in objectives if o.alive and o.active]
                        nearest = None
                        min_dist = 500
                        for t in all_targets:
                            dist = get_distance(player, t)
                            if dist < min_dist:
                                min_dist = dist
                                nearest = t
                        if nearest:
                            player.basic_attack(nearest)
                        attack_move_mode = False
                    else:
                        targets = [m for m in red_minions if m.alive] + [m for m in blue_minions if m.alive and m.was_low_hp]
                        if enemy_hero.alive: targets.append(enemy_hero)
                        if game_mode != "duel":
                            targets += [t for t in towers if t.alive]
                            targets += [n for n in nexuses if n.alive]
                            targets += [j for j in jungle_camps if j.alive]
                            targets += [o for o in objectives if o.alive and o.active]
                        clicked_target = None
                        for t in targets:
                            if t.rect.collidepoint(mouse_pos[0] + camera_x, mouse_pos[1] + camera_y):
                                clicked_target = t
                                break
                        if clicked_target:
                            player.basic_attack(clicked_target)
                            if player.recalling:
                                player.cancel_recall()

        if game_over:
            screen.fill(BG_COLOR)
            font = pygame.font.SysFont("arial", 80, bold=True)
            small_font = pygame.font.SysFont("arial", 24)
            if victory:
                txt = font.render("VICTORY!", True, GOLD_COLOR)
            else:
                txt = font.render("DEFEAT", True, RED_TEAM)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 100))
            gpm = int(player.gold_earned_total / (game_time / 60000)) if game_time > 0 else 0
            minutes = int(game_time // 60000)
            seconds = int((game_time % 60000) // 1000)
            stats = f"K/D/A: {player.kills}/{player.deaths}/{player.assists}  |  LH: {player.last_hits}  |  Lvl: {player.level}  |  GPM: {gpm}  |  Time: {minutes:02d}:{seconds:02d}"
            stats_txt = small_font.render(stats, True, WHITE)
            screen.blit(stats_txt, (WIDTH//2 - stats_txt.get_width()//2, HEIGHT//2))
            restart_txt = small_font.render("Press [R] to Restart", True, WHITE)
            screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, HEIGHT//2 + 60))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        if not shop_open:
            if keys[pygame.K_q]:
                all_enemies = [m for m in red_minions if m.alive]
                if game_mode != "duel":
                    all_enemies += [j for j in jungle_camps if j.alive]
                    all_enemies += [o for o in objectives if o.alive and o.active]
                if enemy_hero.alive: all_enemies.append(enemy_hero)
                player.cast_q(all_enemies, projectiles, mouse_pos, camera_x, camera_y)
            if keys[pygame.K_w]:
                all_enemies = [m for m in red_minions if m.alive]
                if enemy_hero.alive: all_enemies.append(enemy_hero)
                player.cast_w(all_enemies, mouse_pos, camera_x, camera_y)
            if keys[pygame.K_e]:
                all_enemies = [m for m in red_minions if m.alive]
                if enemy_hero.alive: all_enemies.append(enemy_hero)
                player.cast_e(all_enemies, projectiles)
            if keys[pygame.K_r]:
                all_enemies = [m for m in red_minions if m.alive]
                if game_mode != "duel":
                    all_enemies += [j for j in jungle_camps if j.alive]
                    all_enemies += [o for o in objectives if o.alive and o.active]
                if enemy_hero.alive: all_enemies.append(enemy_hero)
                player.cast_r(all_enemies, projectiles, mouse_pos, camera_x, camera_y)

            player.update_base(mouse_pos, camera_x, camera_y)
            if player.attack_target and player.alive:
                player.basic_attack(player.attack_target)
            if player.alive:
                target_camera_x = player.rect.centerx - WIDTH // 2
                target_camera_y = player.rect.centery - HEIGHT // 2
                camera_x = max(0, min(MAP_WIDTH - WIDTH, target_camera_x))
                camera_y = max(0, min(MAP_HEIGHT - HEIGHT, target_camera_y))
            if screen_shake > 0:
                camera_x += random.randint(-screen_shake, screen_shake)
                camera_y += random.randint(-screen_shake, screen_shake)
                screen_shake -= 0.5
            
            enemy_hero.update_base()
            if enemy_hero.alive:
                hp_ratio = enemy_hero.hp / enemy_hero.max_hp
                if hp_ratio < 0.5 and game_mode != "duel":
                    nearest_camp = None
                    min_dist = 500
                    for camp in jungle_camps:
                        if camp.alive:
                            dist = get_distance(enemy_hero, camp)
                            if dist < min_dist:
                                min_dist = dist
                                nearest_camp = camp
                    if nearest_camp and min_dist < 300:
                        enemy_hero.basic_attack(nearest_camp)
                    else:
                        enemy_hero.rect.x += 2
                elif hp_ratio < 0.3:
                    enemy_hero.rect.x += 3
                elif get_distance(enemy_hero, player) < 450 and player.alive:
                    dist_to_player = get_distance(enemy_hero, player)
                    if dist_to_player > 120:
                        dx = player.rect.centerx - enemy_hero.rect.centerx
                        dy = player.rect.centery - enemy_hero.rect.centery
                        dist = math.hypot(dx, dy)
                        enemy_hero.rect.x += (dx/dist) * 3
                        enemy_hero.rect.y += (dy/dist) * 3
                    else:
                        if enemy_hero.r_cd == 0 and enemy_hero.mana >= 80 and hp_ratio > 0.5:
                            enemy_hero.cast_r([player], projectiles)
                        elif enemy_hero.q_cd == 0 and enemy_hero.mana >= 30:
                            enemy_hero.cast_q([player], projectiles)
                        elif enemy_hero.e_cd == 0 and enemy_hero.mana >= 40 and hp_ratio < 0.6:
                            enemy_hero.cast_e([player], projectiles)
                        elif enemy_hero.w_cd == 0 and enemy_hero.mana >= 25:
                            enemy_hero.cast_w([player])
                        else:
                            enemy_hero.basic_attack(player)
                else:
                    enemy_hero.rect.x -= 2

            spawn_timer += dt
            if spawn_timer >= MINION_SPAWN_TIME:
                spawn_timer = 0
                if game_mode == "duel":
                    for i in range(3):
                        blue_minions.append(Minion(200, HEIGHT//2 - 30 + (i * 25), 0, "mid"))
                        red_minions.append(Minion(1000, HEIGHT//2 - 30 + (i * 25), 1, "mid"))
                else:
                    lanes = [("top", 150), ("mid", HEIGHT//2), ("bot", MAP_HEIGHT - 250)]
                    for lane_name, lane_y in lanes:
                        for i in range(3):
                            blue_minions.append(Minion(200, lane_y - 30 + (i * 25), 0, lane_name))
                            red_minions.append(Minion(MAP_WIDTH - 250, lane_y - 30 + (i * 25), 1, lane_name))

            for m in blue_minions:
                enemies = [e for e in red_minions if e.alive]
                if game_mode != "duel":
                    enemies += ([t for t in towers if t.alive and t.team == 1])
                    enemies += ([n for n in nexuses if n.alive and n.team == 1])
                enemies += ([enemy_hero] if enemy_hero.alive else [])
                m.update(enemies)
            for m in red_minions:
                enemies = [e for e in blue_minions if e.alive]
                if game_mode != "duel":
                    enemies += ([t for t in towers if t.alive and t.team == 0])
                    enemies += ([n for n in nexuses if n.alive and n.team == 0])
                enemies += ([player] if player.alive else [])
                m.update(enemies)
            for t in towers:
                if t.team == 0:
                    t.update([e for e in red_minions if e.alive], projectiles)
                else:
                    t.update([e for e in blue_minions if e.alive] + ([player] if player.alive else []), projectiles)
            for j in jungle_camps:
                j.update()
            for obj in objectives:
                obj.update()
            for w in wards:
                w.update()
            all_entities = blue_minions + red_minions + [player, enemy_hero] + towers + nexuses + jungle_camps + objectives
            for p in projectiles:
                p.update(all_entities)
            blue_minions = [m for m in blue_minions if m.alive]
            red_minions = [m for m in red_minions if m.alive]
            projectiles = [p for p in projectiles if p.alive]
            wards = [w for w in wards if w.alive]
            if game_mode == "duel":
                if player.kills >= 5:
                    game_over = True
                    victory = True
                elif enemy_hero.kills >= 5:
                    game_over = True
                    victory = False
            else:
                if not nexuses[0].alive:
                    game_over = True
                    victory = False
                elif not nexuses[1].alive:
                    game_over = True
                    victory = True

        # DRAW
        screen.fill(BG_COLOR)
        if game_mode != "duel":
            pygame.draw.rect(screen, JUNGLE_COLOR, (-camera_x + 600, -camera_y, 400, MAP_HEIGHT))
            pygame.draw.rect(screen, JUNGLE_COLOR, (MAP_WIDTH - 1000 - camera_x, -camera_y, 400, MAP_HEIGHT))
            pygame.draw.rect(screen, LANE_COLOR, (-camera_x, 100 - camera_y, MAP_WIDTH, 80))
            pygame.draw.rect(screen, LANE_COLOR, (-camera_x, HEIGHT//2 - 40 - camera_y, MAP_WIDTH, 80))
            pygame.draw.rect(screen, LANE_COLOR, (-camera_x, MAP_HEIGHT - 290 - camera_y, MAP_WIDTH, 80))
            pygame.draw.rect(screen, (30, 50, 100), (-camera_x, -camera_y, 350, MAP_HEIGHT))
            pygame.draw.rect(screen, (100, 30, 30), (MAP_WIDTH - 350 - camera_x, -camera_y, 350, MAP_HEIGHT))
        else:
            pygame.draw.rect(screen, LANE_COLOR, (-camera_x, HEIGHT//2 - 40 - camera_y, MAP_WIDTH, 80))

        for n in nexuses:
            if n.alive:
                n_rect = n.rect.copy()
                n_rect.x -= camera_x
                n_rect.y -= camera_y
                pygame.draw.rect(screen, n.color, n_rect)
                pygame.draw.rect(screen, GOLD_COLOR, n_rect, 3)
                draw_bars(screen, n, camera_x, camera_y)
        for t in towers:
            if t.alive:
                t_rect = t.rect.copy()
                t_rect.x -= camera_x
                t_rect.y -= camera_y
                pygame.draw.rect(screen, t.color, t_rect)
                if settings["show_range_indicators"]:
                    pygame.draw.circle(screen, WHITE, t_rect.center, TOWER_RANGE, 1)
                draw_bars(screen, t, camera_x, camera_y)
        for j in jungle_camps:
            if j.alive:
                j_rect = j.rect.copy()
                j_rect.x -= camera_x
                j_rect.y -= camera_y
                pygame.draw.rect(screen, j.color, j_rect)
                pygame.draw.circle(screen, WHITE, j_rect.center, 30, 1)
                draw_bars(screen, j, camera_x, camera_y)
                font_small = pygame.font.SysFont("arial", 12, bold=True)
                txt = font_small.render(j.buff_type, True, WHITE)
                screen.blit(txt, (j_rect.centerx - txt.get_width()//2, j_rect.y - 20))
        for obj in objectives:
            if obj.alive:
                obj_rect = obj.rect.copy()
                obj_rect.x -= camera_x
                obj_rect.y -= camera_y
                if obj.active:
                    pygame.draw.rect(screen, obj.color, obj_rect)
                    pygame.draw.circle(screen, WHITE, obj_rect.center, 40, 2)
                    draw_bars(screen, obj, camera_x, camera_y)
                    font_small = pygame.font.SysFont("arial", 14, bold=True)
                    txt = font_small.render(obj.obj_type.upper(), True, WHITE)
                    screen.blit(txt, (obj_rect.centerx - txt.get_width()//2, obj_rect.y - 25))
                else:
                    pygame.draw.rect(screen, (50, 50, 50), obj_rect)
                    remaining = max(0, obj.spawn_time - obj.game_time)
                    mins = int(remaining // 60000)
                    secs = int((remaining % 60000) // 1000)
                    font_small = pygame.font.SysFont("arial", 12, bold=True)
                    txt = font_small.render(f"{mins}:{secs:02d}", True, WHITE)
                    screen.blit(txt, (obj_rect.centerx - txt.get_width()//2, obj_rect.centery - 6))
        for w in wards:
            if w.alive:
                w_rect = w.rect.copy()
                w_rect.x -= camera_x
                w_rect.y -= camera_y
                pygame.draw.circle(screen, WARD_COLOR[:3], w_rect.center, 5)
                pygame.draw.circle(screen, WARD_COLOR[:3], w_rect.center, w.vision_range, 1)
        for m in blue_minions + red_minions:
            m_rect = m.rect.copy()
            m_rect.x -= camera_x
            m_rect.y -= camera_y
            pygame.draw.rect(screen, m.color, m_rect)
            if m.team == 0 and m.hp < (m.max_hp * 0.20):
                pygame.draw.rect(screen, GOLD_COLOR, m_rect, 2)
            if m.stun_timer > 0:
                pygame.draw.circle(screen, STUN_COLOR, m_rect.center, 15, 2)
            if m.slow_timer > 0:
                pygame.draw.circle(screen, SLOW_COLOR, m_rect.center, 15, 2)
            if m.root_timer > 0:
                pygame.draw.circle(screen, ROOT_COLOR, m_rect.center, 15, 2)
            draw_bars(screen, m, camera_x, camera_y)
        for p in projectiles:
            pygame.draw.circle(screen, p.color, (int(p.x - camera_x), int(p.y - camera_y)), p.radius)
        if player.alive:
            p_rect = player.rect.copy()
            p_rect.x -= camera_x
            p_rect.y -= camera_y
            pygame.draw.circle(screen, player.hero_color, p_rect.center, 15)
            if settings["show_range_indicators"]:
                pygame.draw.circle(screen, WHITE, p_rect.center, player.attack_range, 1)
            if player.shield_active > 0:
                pygame.draw.circle(screen, MANA_BLUE, p_rect.center, 22, 2)
            if player.stun_timer > 0:
                pygame.draw.circle(screen, STUN_COLOR, p_rect.center, 25, 2)
            if player.slow_timer > 0:
                pygame.draw.circle(screen, SLOW_COLOR, p_rect.center, 25, 2)
            if player.root_timer > 0:
                pygame.draw.circle(screen, ROOT_COLOR, p_rect.center, 25, 2)
            if player.drake_buff > 0:
                pygame.draw.circle(screen, DRAKE_COLOR, p_rect.center, 28, 2)
            if player.titan_buff > 0:
                pygame.draw.circle(screen, TITAN_COLOR, p_rect.center, 31, 2)
            if player.recalling:
                pygame.draw.circle(screen, MANA_BLUE, p_rect.center, 30, 3)
                recall_pct = 1 - (player.recall_timer / RECALL_TIME)
                pygame.draw.arc(pygame.Rect(p_rect.centerx - 30, p_rect.centery - 30, 60, 60), 0, recall_pct * 6.28, 3, MANA_BLUE)
            draw_bars(screen, player, camera_x, camera_y)
            if player.move_target:
                target_x = player.move_target[0] - camera_x
                target_y = player.move_target[1] - camera_y
                pygame.draw.circle(screen, GREEN, (int(target_x), int(target_y)), 5, 2)
        if enemy_hero.alive:
            e_rect = enemy_hero.rect.copy()
            e_rect.x -= camera_x
            e_rect.y -= camera_y
            pygame.draw.circle(screen, enemy_hero.hero_color, e_rect.center, 15)
            if enemy_hero.shield_active > 0:
                pygame.draw.circle(screen, MANA_BLUE, e_rect.center, 22, 2)
            if enemy_hero.bounty > 0:
                bounty_font = pygame.font.SysFont("arial", 12, bold=True)
                bounty_txt = bounty_font.render(f"${enemy_hero.bounty}", True, BOUNTY_COLOR)
                screen.blit(bounty_txt, (e_rect.centerx - bounty_txt.get_width()//2, e_rect.y - 30))
            draw_bars(screen, enemy_hero, camera_x, camera_y)

        update_draw_particles(screen, camera_x, camera_y)
        update_draw_text_effects(screen, camera_x, camera_y)
        update_draw_kill_feed(screen)
        draw_fog(screen, player, blue_minions, wards, camera_x, camera_y)

        minutes = int(game_time // 60000)
        seconds = int((game_time % 60000) // 1000)
        timer_font = pygame.font.SysFont("arial", 24, bold=True)
        timer_text = f"{minutes:02d}:{seconds:02d}"
        timer_surf = timer_font.render(timer_text, True, WHITE)
        screen.blit(timer_surf, (WIDTH//2 - timer_surf.get_width()//2, 10))

        font = pygame.font.SysFont("arial", 20, bold=True)
        gpm = int(player.gold_earned_total / (game_time / 60000)) if game_time > 0 else 0
        ui_text = f"Gold: {player.gold}  |  LH: {player.last_hits}  |  Denies: {player.denies}  |  K/D/A: {player.kills}/{player.deaths}/{player.assists}  |  GPM: {gpm}"
        screen.blit(font.render(ui_text, True, GOLD_COLOR), (10, 10))
        level_font = pygame.font.SysFont("arial", 16, bold=True)
        lvl_txt = f"Lvl {player.level}  XP: {player.xp}/{player.xp_to_next}  |  Wards: {player.ward_count}/{MAX_WARDS}  |  Potions: {player.potion_count}"
        if player.upgrades_available > 0:
            lvl_txt += f"  |  UPGRADES: {player.upgrades_available}"
        screen.blit(level_font.render(lvl_txt, True, PURPLE), (10, 35))
        passive_font = pygame.font.SysFont("arial", 12, bold=True)
        passive_txt = passive_font.render(f"Passive: {player.passive_desc}", True, PASSIVE_COLOR)
        screen.blit(passive_txt, (10, 75))
        pygame.draw.rect(screen, BLACK, (10, 90, 200, 8))
        xp_ratio = player.xp / player.xp_to_next if player.level < MAX_LEVEL else 1
        pygame.draw.rect(screen, PURPLE, (10, 90, 200 * xp_ratio, 8))
        cd_font = pygame.font.SysFont("arial", 14)
        q_txt = f"[Q] {'Heal' if player.hero_type == 'support' else 'Ability'} {'(Ready)' if player.q_cd == 0 else f'({player.q_cd//60}s)'}"
        w_txt = f"[W] Ability    {'(Ready)' if player.w_cd == 0 else f'({player.w_cd//60}s)'}"
        e_txt = f"[E] Ability    {'(Ready)' if player.e_cd == 0 else f'({player.e_cd//60}s)'}"
        r_txt = f"[R] Ultimate   {'(Ready)' if player.r_cd == 0 else f'({player.r_cd//60}s)'}"
        f_txt = f"[F] Potion ({player.potion_count})"
        screen.blit(cd_font.render(q_txt, True, MANA_BLUE if player.q_cd == 0 else WHITE), (10, HEIGHT - 100))
        screen.blit(cd_font.render(w_txt, True, MANA_BLUE if player.w_cd == 0 else WHITE), (10, HEIGHT - 80))
        screen.blit(cd_font.render(e_txt, True, MANA_BLUE if player.e_cd == 0 else WHITE), (10, HEIGHT - 60))
        screen.blit(cd_font.render(r_txt, True, GOLD_COLOR if player.r_cd == 0 else WHITE), (10, HEIGHT - 40))
        screen.blit(cd_font.render(f_txt, True, GREEN if player.potion_count > 0 else WHITE), (10, HEIGHT - 20))
        inst = cd_font.render("Right-Click: Move | Left-Click: Attack | Q/W/E/R: Abilities | B (Hold): Recall | V: Ward", True, WHITE)
        screen.blit(inst, (WIDTH//2 - 350, HEIGHT - 10))

        if not player.alive:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            respawn_font = pygame.font.SysFont("arial", 40, bold=True)
            txt = respawn_font.render(f"Respawning in {int(player.respawn_timer/1000) + 1}s", True, WHITE)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 20))

        if shop_open:
            shop_surf = pygame.Surface((700, 550), pygame.SRCALPHA)
            shop_surf.fill((10, 10, 20, 230))
            screen.blit(shop_surf, (WIDTH//2 - 350, HEIGHT//2 - 275))
            title = font.render("ITEM SHOP", True, GOLD_COLOR)
            screen.blit(title, (WIDTH//2 - 60, HEIGHT//2 - 255))
            items = [
                (f"[1] Broad Sword (+30 AD) - 400g", player.has_sword, 400),
                (f"[2] Swift Boots (+2 Speed) - 300g", player.has_boots, 300),
                (f"[3] Mana Crystal (+50 Mana) - 500g", player.has_mana_crystal, 500),
                (f"[4] Chainmail (+300 HP) - 600g", player.has_armor, 600),
                (f"[5] Vampiric Edge (+15% LS) - 700g", player.has_lifesteal, 700),
                (f"[6] Ward (Place vision) - 100g", False, 100),
                (f"[7] Magic Cloak (+20% MR) - 500g", player.has_magic_resist, 500),
                (f"[8] Chrono Crystal (-20% CD) - 800g", player.has_cooldown_reduction, 800),
                (f"[9] Health Potion (+200 HP) - 150g", False, 150),
            ]
            for i, (item_text, owned, cost) in enumerate(items):
                display_text = f"{item_text} {'(Owned)' if owned else ''}"
                color = GREEN if not owned and player.gold >= cost else (100, 100, 100)
                screen.blit(cd_font.render(display_text, True, color), (WIDTH//2 - 330, HEIGHT//2 - 210 + i * 35))
            close_txt = cd_font.render("Press [B] or [ESC] to close | [S] Sell item", True, WHITE)
            screen.blit(close_txt, (WIDTH//2 - 160, HEIGHT//2 + 230))

        draw_minimap(screen, player, enemy_hero, blue_minions, red_minions, towers, nexuses, jungle_camps, wards, objectives)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
