import pygame
import sys
import array
import math

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# --- ГЕНЕРАЦИЯ 8-БИТНЫХ ЗВУКОВ ---
def create_sound(freq, duration_ms, volume=0.2, tone_type="square"):
    sample_rate = 22050
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    buf = array.array('h')
    
    for i in range(num_samples):
        t = float(i) / sample_rate
        if tone_type == "square":
            val = 32767 if (int(t * freq * 2) % 2 == 0) else -32768
        else:
            val = int((2.0 * (t * freq - math.floor(0.5 + t * freq))) * 32767)
            
        fade = 1.0 - (i / num_samples)
        buf.append(int(val * volume * fade))
        
    return pygame.mixer.Sound(buffer=buf)

sound_stunt = create_sound(freq=587.33, duration_ms=60, volume=0.15, tone_type="square")
sound_crash = create_sound(freq=120, duration_ms=300, volume=0.3, tone_type="saw")

# --- НАСТРОЙКИ ЭКРАНА ---
V_WIDTH, V_HEIGHT = 320, 570
virtual_screen = pygame.Surface((V_WIDTH, V_HEIGHT))

info = pygame.display.Info()
real_w = max(info.current_w, 360)
real_h = max(info.current_h, 640)
screen = pygame.display.set_mode((real_w, real_h), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# --- СОСТОЯНИЕ ИГРОКА И МАГАЗИНА ---
total_coins = 1000

# Транспорт
owned_scooters = ['default']
equipped_scooter = 'default'
scooter_bar_color = (200, 200, 200)
scooter_fork_color = (100, 100, 100)

# Трюки
owned_poses = ['default']
equipped_pose = 'default'

# Персонаж (Скины)
owned_skins = ['default']
equipped_skin = 'default'
skin_body_color = (30, 30, 30)

shop_tab = 'main'

def reset_game():
    return {
        'angle': 0,
        'score': 0,
        'game_over': False,
        'is_stunting': False,
        'played_crash_sound': False
    }

sound_enabled = True
difficulty = "Нормально"

current_state = 'menu'
game_state = reset_game()

ground_y = 380
rear_wheel_x = 90

bg_scroll = 0

# --- КНОПКИ ---
btn_w, btn_h = 135, 65
btn_stunt = pygame.Rect(15, 485, btn_w, btn_h)
btn_brake = pygame.Rect(170, 485, btn_w, btn_h)
btn_restart = pygame.Rect(80, 280, 160, 50)

# Главное меню
btn_play = pygame.Rect(60, 230, 200, 55)
btn_settings = pygame.Rect(60, 300, 200, 55)
btn_shop = pygame.Rect(60, 370, 200, 55)

# Настройки
btn_diff = pygame.Rect(40, 220, 240, 50)
btn_sound = pygame.Rect(40, 285, 240, 50)
btn_back_sett = pygame.Rect(80, 370, 160, 50)

# Магазин
btn_shop_character = pygame.Rect(30, 170, 260, 40)

btn_shop_scooter = pygame.Rect(15, 225, 85, 40)
btn_shop_scooter_tricks = pygame.Rect(15, 270, 85, 30)

btn_shop_bike = pygame.Rect(117, 225, 85, 40)
btn_shop_bike_tricks = pygame.Rect(117, 270, 85, 30)

btn_shop_moto = pygame.Rect(220, 225, 85, 40)
btn_shop_moto_tricks = pygame.Rect(220, 270, 85, 30)

btn_back_shop = pygame.Rect(80, 430, 160, 45)

# Списки в магазине
btn_item_1 = pygame.Rect(30, 210, 260, 45)
btn_item_2 = pygame.Rect(30, 265, 260, 45)
btn_item_3 = pygame.Rect(30, 320, 260, 45)

font_large = pygame.font.SysFont(None, 32)
font_btn = pygame.font.SysFont(None, 18)
font_btn_med = pygame.font.SysFont(None, 22)
font_title = pygame.font.SysFont(None, 36)

stunt_sound_timer = 0

running = True
while running:
    virtual_screen.fill((135, 206, 235))

    mouse_click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            mouse_click = True

    mouse_pressed = pygame.mouse.get_pressed()[0]
    raw_mx, raw_my = pygame.mouse.get_pos()
    mx = int(raw_mx * (V_WIDTH / real_w))
    my = int(raw_my * (V_HEIGHT / real_h))
    keys = pygame.key.get_pressed()

    # ==================== 1. ГЛАВНОЕ МЕНЮ ====================
    if current_state == 'menu':
        title_txt = font_title.render("STUNT SCOOTER", True, (255, 120, 0))
        virtual_screen.blit(title_txt, (V_WIDTH // 2 - title_txt.get_width() // 2, 130))

        pygame.draw.rect(virtual_screen, (0, 180, 80), btn_play, border_radius=14)
        pygame.draw.rect(virtual_screen, (70, 130, 180), btn_settings, border_radius=14)
        pygame.draw.rect(virtual_screen, (230, 150, 30), btn_shop, border_radius=14)

        play_txt = font_btn_med.render("ИГРАТЬ", True, (255, 255, 255))
        sett_txt = font_btn_med.render("НАСТРОЙКИ", True, (255, 255, 255))
        shop_txt = font_btn_med.render("МАГАЗИН", True, (255, 255, 255))

        virtual_screen.blit(play_txt, play_txt.get_rect(center=btn_play.center))
        virtual_screen.blit(sett_txt, sett_txt.get_rect(center=btn_settings.center))
        virtual_screen.blit(shop_txt, shop_txt.get_rect(center=btn_shop.center))

        if mouse_click:
            if btn_play.collidepoint(mx, my):
                game_state = reset_game()
                current_state = 'game'
            elif btn_settings.collidepoint(mx, my):
                current_state = 'settings'
            elif btn_shop.collidepoint(mx, my):
                shop_tab = 'main'
                current_state = 'shop'

    # ==================== 2. НАСТРОЙКИ ====================
    elif current_state == 'settings':
        title_txt = font_title.render("НАСТРОЙКИ", True, (50, 50, 50))
        virtual_screen.blit(title_txt, (V_WIDTH // 2 - title_txt.get_width() // 2, 130))

        pygame.draw.rect(virtual_screen, (100, 100, 100), btn_diff, border_radius=12)
        pygame.draw.rect(virtual_screen, (100, 100, 100), btn_sound, border_radius=12)
        pygame.draw.rect(virtual_screen, (200, 60, 60), btn_back_sett, border_radius=12)

        diff_txt = font_btn_med.render(f"Сложность: {difficulty}", True, (255, 255, 255))
        sound_txt = font_btn_med.render(f"Звук: {'ВКЛ' if sound_enabled else 'ВЫКЛ'}", True, (255, 255, 255))
        back_txt = font_btn_med.render("НАЗАД", True, (255, 255, 255))

        virtual_screen.blit(diff_txt, diff_txt.get_rect(center=btn_diff.center))
        virtual_screen.blit(sound_txt, sound_txt.get_rect(center=btn_sound.center))
        virtual_screen.blit(back_txt, back_txt.get_rect(center=btn_back_sett.center))

        if mouse_click:
            if btn_diff.collidepoint(mx, my):
                if difficulty == "Легко":
                    difficulty = "Нормально"
                elif difficulty == "Нормально":
                    difficulty = "Хардкор"
                else:
                    difficulty = "Легко"
            elif btn_sound.collidepoint(mx, my):
                sound_enabled = not sound_enabled
            elif btn_back_sett.collidepoint(mx, my):
                current_state = 'menu'

    # ==================== 3. МАГАЗИН ====================
    elif current_state == 'shop':
        title_txt = font_title.render("МАГАЗИН", True, (230, 150, 30))
        virtual_screen.blit(title_txt, (V_WIDTH // 2 - title_txt.get_width() // 2, 70))

        coins_txt = font_large.render(f"Монеты: {total_coins}", True, (0, 0, 0))
        virtual_screen.blit(coins_txt, (V_WIDTH // 2 - coins_txt.get_width() // 2, 115))

        if shop_tab == 'main':
            pygame.draw.rect(virtual_screen, (160, 50, 210), btn_shop_character, border_radius=10)
            pygame.draw.rect(virtual_screen, (255, 255, 255), btn_shop_character, width=2, border_radius=10)
            t_char = font_btn_med.render("ПЕРСОНАЖ (Скины)", True, (255, 255, 255))
            virtual_screen.blit(t_char, t_char.get_rect(center=btn_shop_character.center))

            pygame.draw.rect(virtual_screen, (50, 120, 200), btn_shop_scooter, border_radius=8)
            t_sc = font_btn.render("самокат", True, (255, 255, 255))
            virtual_screen.blit(t_sc, t_sc.get_rect(center=btn_shop_scooter.center))

            pygame.draw.rect(virtual_screen, (40, 40, 40), btn_shop_scooter_tricks, border_radius=6)
            t_sct = font_btn.render("трюки", True, (255, 255, 255))
            virtual_screen.blit(t_sct, t_sct.get_rect(center=btn_shop_scooter_tricks.center))

            pygame.draw.rect(virtual_screen, (50, 120, 200), btn_shop_bike, border_radius=8)
            t_bk = font_btn.render("велик", True, (255, 255, 255))
            virtual_screen.blit(t_bk, t_bk.get_rect(center=btn_shop_bike.center))

            pygame.draw.rect(virtual_screen, (40, 40, 40), btn_shop_bike_tricks, border_radius=6)
            t_bkt = font_btn.render("трюки", True, (255, 255, 255))
            virtual_screen.blit(t_bkt, t_bkt.get_rect(center=btn_shop_bike_tricks.center))

            pygame.draw.rect(virtual_screen, (50, 120, 200), btn_shop_moto, border_radius=8)
            t_mt = font_btn.render("мотоцикл", True, (255, 255, 255))
            virtual_screen.blit(t_mt, t_mt.get_rect(center=btn_shop_moto.center))

            pygame.draw.rect(virtual_screen, (40, 40, 40), btn_shop_moto_tricks, border_radius=6)
            t_mtt = font_btn.render("трюки", True, (255, 255, 255))
            virtual_screen.blit(t_mtt, t_mtt.get_rect(center=btn_shop_moto_tricks.center))

            pygame.draw.rect(virtual_screen, (200, 60, 60), btn_back_shop, border_radius=12)
            back_txt = font_btn_med.render("НАЗАД", True, (255, 255, 255))
            virtual_screen.blit(back_txt, back_txt.get_rect(center=btn_back_shop.center))

            if mouse_click:
                if btn_shop_character.collidepoint(mx, my):
                    shop_tab = 'character'
                elif btn_shop_scooter.collidepoint(mx, my):
                    shop_tab = 'scooter_list'
                elif btn_shop_scooter_tricks.collidepoint(mx, my):
                    shop_tab = 'scooter_tricks'
                elif btn_shop_bike.collidepoint(mx, my):
                    shop_tab = 'bike_list'
                elif btn_shop_bike_tricks.collidepoint(mx, my):
                    shop_tab = 'bike_tricks'
                elif btn_shop_moto.collidepoint(mx, my):
                    shop_tab = 'moto_list'
                elif btn_shop_moto_tricks.collidepoint(mx, my):
                    shop_tab = 'moto_tricks'
                elif btn_back_shop.collidepoint(mx, my):
                    current_state = 'menu'

        elif shop_tab == 'character':
            sub_title = font_btn_med.render("— Скины Персонажа —", True, (50, 50, 50))
            virtual_screen.blit(sub_title, (V_WIDTH // 2 - sub_title.get_width() // 2, 160))

            c1 = (0, 180, 80) if equipped_skin == 'default' else (120, 120, 120)
            pygame.draw.rect(virtual_screen, c1, btn_item_1, border_radius=12)
            lbl1 = "Классик (Надет)" if equipped_skin == 'default' else "Классик (Выбрать)"
            t1 = font_btn_med.render(lbl1, True, (255, 255, 255))
            virtual_screen.blit(t1, t1.get_rect(center=btn_item_1.center))

            c2 = (0, 180, 80) if equipped_skin == 'skater' else ((160, 50, 210) if 'skater' in owned_skins else (100, 100, 100))
            pygame.draw.rect(virtual_screen, c2, btn_item_2, border_radius=12)
            lbl2 = "Скейтер (Надет)" if equipped_skin == 'skater' else ("Скейтер (Выбрать)" if 'skater' in owned_skins else "Скейтер (Кепка) - 500")
            t2 = font_btn_med.render(lbl2, True, (255, 255, 255))
            virtual_screen.blit(t2, t2.get_rect(center=btn_item_2.center))

            c3 = (0, 180, 80) if equipped_skin == 'cyber' else ((0, 200, 220) if 'cyber' in owned_skins else (100, 100, 100))
            pygame.draw.rect(virtual_screen, c3, btn_item_3, border_radius=12)
            lbl3 = "Кибер-Райдер (Надет)" if equipped_skin == 'cyber' else ("Кибер-Райдер (Выбрать)" if 'cyber' in owned_skins else "Кибер (Рюкзак) - 1200")
            t3 = font_btn_med.render(lbl3, True, (255, 255, 255))
            virtual_screen.blit(t3, t3.get_rect(center=btn_item_3.center))

            pygame.draw.rect(virtual_screen, (200, 60, 60), btn_back_shop, border_radius=12)
            back_txt = font_btn_med.render("НАЗАД", True, (255, 255, 255))
            virtual_screen.blit(back_txt, back_txt.get_rect(center=btn_back_shop.center))

            if mouse_click:
                if btn_item_1.collidepoint(mx, my):
                    equipped_skin = 'default'
                    skin_body_color = (30, 30, 30)
                elif btn_item_2.collidepoint(mx, my):
                    if 'skater' not in owned_skins and total_coins >= 500:
                        total_coins -= 500
                        owned_skins.append('skater')
                        equipped_skin = 'skater'
                        skin_body_color = (40, 80, 200) # Синяя худи
                    elif 'skater' in owned_skins:
                        equipped_skin = 'skater'
                        skin_body_color = (40, 80, 200)
                elif btn_item_3.collidepoint(mx, my):
                    if 'cyber' not in owned_skins and total_coins >= 1200:
                        total_coins -= 1200
                        owned_skins.append('cyber')
                        equipped_skin = 'cyber'
                        skin_body_color = (255, 0, 150) # Неоновая куртка
                    elif 'cyber' in owned_skins:
                        equipped_skin = 'cyber'
                        skin_body_color = (255, 0, 150)
                elif btn_back_shop.collidepoint(mx, my):
                    shop_tab = 'main'

        elif shop_tab == 'scooter_list':
            sub_title = font_btn_med.render("— Модели Самокатов —", True, (50, 50, 50))
            virtual_screen.blit(sub_title, (V_WIDTH // 2 - sub_title.get_width() // 2, 160))

            c1 = (0, 180, 80) if equipped_scooter == 'default' else (120, 120, 120)
            pygame.draw.rect(virtual_screen, c1, btn_item_1, border_radius=12)
            lbl1 = "Классик (Надет)" if equipped_scooter == 'default' else "Классик (Выбрать)"
            t1 = font_btn_med.render(lbl1, True, (255, 255, 255))
            virtual_screen.blit(t1, t1.get_rect(center=btn_item_1.center))

            c2 = (0, 180, 80) if equipped_scooter == 'neon_pro' else ((140, 60, 220) if 'neon_pro' in owned_scooters else (100, 100, 100))
            pygame.draw.rect(virtual_screen, c2, btn_item_2, border_radius=12)
            lbl2 = "Neon Pro (Надет)" if equipped_scooter == 'neon_pro' else ("Neon Pro (Выбрать)" if 'neon_pro' in owned_scooters else "Neon Pro - 800 монет")
            t2 = font_btn_med.render(lbl2, True, (255, 255, 255))
            virtual_screen.blit(t2, t2.get_rect(center=btn_item_2.center))

            pygame.draw.rect(virtual_screen, (200, 60, 60), btn_back_shop, border_radius=12)
            back_txt = font_btn_med.render("НАЗАД", True, (255, 255, 255))
            virtual_screen.blit(back_txt, back_txt.get_rect(center=btn_back_shop.center))

            if mouse_click:
                if btn_item_1.collidepoint(mx, my):
                    equipped_scooter = 'default'
                    scooter_bar_color = (200, 200, 200)
                    scooter_fork_color = (100, 100, 100)
                elif btn_item_2.collidepoint(mx, my):
                    if 'neon_pro' not in owned_scooters and total_coins >= 800:
                        total_coins -= 800
                        owned_scooters.append('neon_pro')
                        equipped_scooter = 'neon_pro'
                        scooter_bar_color = (50, 255, 100)
                        scooter_fork_color = (180, 50, 230)
                    elif 'neon_pro' in owned_scooters:
                        equipped_scooter = 'neon_pro'
                        scooter_bar_color = (50, 255, 100)
                        scooter_fork_color = (180, 50, 230)
                elif btn_back_shop.collidepoint(mx, my):
                    shop_tab = 'main'

        elif shop_tab == 'scooter_tricks':
            sub_title = font_btn_med.render("— Трюки для Самоката —", True, (50, 50, 50))
            virtual_screen.blit(sub_title, (V_WIDTH // 2 - sub_title.get_width() // 2, 160))

            c_def = (0, 180, 80) if equipped_pose == 'default' else (120, 120, 120)
            pygame.draw.rect(virtual_screen, c_def, btn_item_1, border_radius=12)
            lbl_def = "Стандарт (Надет)" if equipped_pose == 'default' else "Стандарт (Выбрать)"
            t_def = font_btn_med.render(lbl_def, True, (255, 255, 255))
            virtual_screen.blit(t_def, t_def.get_rect(center=btn_item_1.center))

            c_of = (0, 180, 80) if equipped_pose == 'one_foot' else ((180, 50, 230) if 'one_foot' in owned_poses else (100, 100, 100))
            pygame.draw.rect(virtual_screen, c_of, btn_item_2, border_radius=12)
            lbl_of = "One Foot (Надет)" if equipped_pose == 'one_foot' else ("One Foot (Выбрать)" if 'one_foot' in owned_poses else "One Foot - 600 монет")
            t_of = font_btn_med.render(lbl_of, True, (255, 255, 255))
            virtual_screen.blit(t_of, t_of.get_rect(center=btn_item_2.center))

            c_nh = (0, 180, 80) if equipped_pose == 'no_hand' else ((255, 140, 0) if 'no_hand' in owned_poses else (100, 100, 100))
            pygame.draw.rect(virtual_screen, c_nh, btn_item_3, border_radius=12)
            lbl_nh = "No Hand (Надет)" if equipped_pose == 'no_hand' else ("No Hand (Выбрать)" if 'no_hand' in owned_poses else "No Hand - 1500 монет")
            t_nh = font_btn_med.render(lbl_nh, True, (255, 255, 255))
            virtual_screen.blit(t_nh, t_nh.get_rect(center=btn_item_3.center))

            pygame.draw.rect(virtual_screen, (200, 60, 60), btn_back_shop, border_radius=12)
            back_txt = font_btn_med.render("НАЗАД", True, (255, 255, 255))
            virtual_screen.blit(back_txt, back_txt.get_rect(center=btn_back_shop.center))

            if mouse_click:
                if btn_item_1.collidepoint(mx, my):
                    equipped_pose = 'default'
                elif btn_item_2.collidepoint(mx, my):
                    if 'one_foot' not in owned_poses and total_coins >= 600:
                        total_coins -= 600
                        owned_poses.append('one_foot')
                        equipped_pose = 'one_foot'
                    elif 'one_foot' in owned_poses:
                        equipped_pose = 'one_foot'
                elif btn_item_3.collidepoint(mx, my):
                    if 'no_hand' not in owned_poses and total_coins >= 1500:
                        total_coins -= 1500
                        owned_poses.append('no_hand')
                        equipped_pose = 'no_hand'
                    elif 'no_hand' in owned_poses:
                        equipped_pose = 'no_hand'
                elif btn_back_shop.collidepoint(mx, my):
                    shop_tab = 'main'

        else:
            txt_stub = font_btn_med.render("В разработке...", True, (80, 80, 80))
            virtual_screen.blit(txt_stub, (V_WIDTH // 2 - txt_stub.get_width() // 2, 250))

            pygame.draw.rect(virtual_screen, (200, 60, 60), btn_back_shop, border_radius=12)
            back_txt = font_btn_med.render("НАЗАД", True, (255, 255, 255))
            virtual_screen.blit(back_txt, back_txt.get_rect(center=btn_back_shop.center))

            if mouse_click and btn_back_shop.collidepoint(mx, my):
                shop_tab = 'main'

    # ==================== 4. ИГРОВОЙ ПРОЦЕСС ====================
    elif current_state == 'game':
        stunt_speed = 2.0 if difficulty == "Легко" else (3.0 if difficulty == "Нормально" else 4.5)
        max_angle = 90 if difficulty == "Легко" else (80 if difficulty == "Нормально" else 70)

        if not game_state['game_over']:
            bg_scroll += 4
            stunt_pressed = (mouse_pressed and btn_stunt.collidepoint(mx, my)) or keys[pygame.K_UP]
            brake_pressed = (mouse_pressed and btn_brake.collidepoint(mx, my)) or keys[pygame.K_DOWN]

            if stunt_pressed:
                game_state['angle'] += stunt_speed
                game_state['is_stunting'] = True

                pts = 4 if equipped_pose == 'one_foot' else (6 if equipped_pose == 'no_hand' else 2)
                game_state['score'] += pts
                total_coins += pts

                if sound_enabled:
                    stunt_sound_timer += 1
                    if stunt_sound_timer % 10 == 0:
                        sound_stunt.play()

                if game_state['angle'] > max_angle:
                    game_state['game_over'] = True

            elif brake_pressed:
                if game_state['angle'] > 0:
                    game_state['angle'] -= 6.0
                game_state['is_stunting'] = False
            else:
                if game_state['angle'] > 0:
                    game_state['angle'] -= 2.0
                game_state['is_stunting'] = False

            if game_state['angle'] < 0:
                game_state['angle'] = 0

        else:
            if sound_enabled and not game_state['played_crash_sound']:
                sound_crash.play()
                game_state['played_crash_sound'] = True

            if mouse_click and btn_restart.collidepoint(mx, my):
                game_state = reset_game()

        # ЗАДНИЙ ФОН
        cloud_shift = (bg_scroll // 4) % (V_WIDTH + 100)
        for cx in [-50, 120, 280]:
            x_pos = (cx - cloud_shift) % (V_WIDTH + 100) - 50
            pygame.draw.circle(virtual_screen, (255, 255, 255), (int(x_pos), 70), 18)
            pygame.draw.circle(virtual_screen, (255, 255, 255), (int(x_pos + 15), 65), 22)
            pygame.draw.circle(virtual_screen, (255, 255, 255), (int(x_pos + 32), 70), 16)

        city_shift = (bg_scroll // 2) % 180
        for bx in range(-180, V_WIDTH + 180, 40):
            x_pos = bx - city_shift
            h = 50 + ((bx * 7) % 40)
            pygame.draw.rect(virtual_screen, (110, 170, 210), (x_pos, ground_y - h, 38, h))

        tree_shift = (bg_scroll) % 160
        for tx in range(-160, V_WIDTH + 160, 80):
            x_pos = tx - tree_shift
            pygame.draw.rect(virtual_screen, (100, 60, 30), (x_pos + 12, ground_y - 45, 6, 45))
            pygame.draw.circle(virtual_screen, (34, 139, 34), (x_pos + 15, ground_y - 50), 18)

        # Дорога
        pygame.draw.rect(virtual_screen, (70, 70, 70), (0, ground_y, V_WIDTH, 90))
        pygame.draw.rect(virtual_screen, (50, 150, 50), (0, 470, V_WIDTH, 100))

        line_offset = bg_scroll % 40
        for lx in range(-40, V_WIDTH + 40, 40):
            pygame.draw.rect(virtual_screen, (255, 255, 255), (lx - line_offset, ground_y + 40, 20, 5))

        # --- САМОКАТ И РАЙДЕР ---
        sc_w, sc_h = 120, 100
        scooter_surf = pygame.Surface((sc_w, sc_h), pygame.SRCALPHA)
        pivot_x, pivot_y = 22, 90

        # Колеса
        pygame.draw.circle(scooter_surf, (20, 20, 20), (pivot_x, pivot_y), 10)
        pygame.draw.circle(scooter_surf, (180, 180, 180), (pivot_x, pivot_y), 5)
        pygame.draw.circle(scooter_surf, (20, 20, 20), (82, 90), 10)
        pygame.draw.circle(scooter_surf, (180, 180, 180), (82, 90), 5)

        # Дека
        pygame.draw.polygon(scooter_surf, (40, 40, 40), [(12, 85), (78, 85), (75, 80), (15, 80)])
        pygame.draw.line(scooter_surf, (10, 10, 10), (16, 80), (74, 80), 2)

        # Руль
        pygame.draw.line(scooter_surf, scooter_fork_color, (78, 86), (75, 68), 4)
        pygame.draw.line(scooter_surf, (50, 50, 50), (75, 68), (73, 62), 6)
        pygame.draw.line(scooter_surf, scooter_bar_color, (73, 62), (73, 35), 4)
        pygame.draw.line(scooter_surf, scooter_bar_color, (62, 35), (84, 35), 4)
        pygame.draw.circle(scooter_surf, (10, 10, 10), (62, 35), 3)
        pygame.draw.circle(scooter_surf, (10, 10, 10), (84, 35), 3)

        pygame.draw.line(scooter_surf, (80, 80, 80), (22, 83), (16, 87), 3)

        # --- ОТРИСОВКА РАЙДЕРА И АКСЕССУАРОВ ---
        head_pos = (52, 12)
        skin_head_color = (255, 205, 178) # Единый цвет кожи
        body_start = (52, 20)
        body_end = (48, 52)

        # 1. МОЩНЫЙ КИБЕР-РЮКЗАК (на спине)
        if equipped_skin == 'cyber':
            pygame.draw.rect(scooter_surf, (30, 30, 40), (36, 22, 10, 18), border_radius=3)
            pygame.draw.rect(scooter_surf, (0, 255, 220), (38, 25, 6, 12), border_radius=2) # Неоновые полосы
            pygame.draw.circle(scooter_surf, (255, 0, 150), (41, 31), 2)

        # 2. ТЕЛО
        pygame.draw.line(scooter_surf, skin_body_color, body_start, body_end, 5)

        # 3. ГОЛОВА (ЦВЕТ КОЖИ)
        pygame.draw.circle(scooter_surf, skin_head_color, head_pos, 7)

        # 4. КРАСНАЯ КЕПКА (АКСЕССУАР СКЕЙТЕРА)
        if equipped_skin == 'skater':
            # Кепка
            pygame.draw.arc(scooter_surf, (220, 40, 40), (44, 4, 16, 12), 0, 3.14, 4)
            # Козырек назад
            pygame.draw.line(scooter_surf, (220, 40, 40), (46, 10), (38, 12), 3)

        # Руки
        if equipped_pose == 'no_hand':
            pygame.draw.line(scooter_surf, skin_body_color, (52, 25), (73, 35), 3)
            if game_state['is_stunting']:
                pygame.draw.line(scooter_surf, skin_body_color, (52, 25), (32, 5), 3)
            else:
                pygame.draw.line(scooter_surf, skin_body_color, (52, 25), (38, 48), 3)
        else:
            pygame.draw.line(scooter_surf, skin_body_color, (52, 25), (73, 35), 3)

        # Ноги
        pygame.draw.line(scooter_surf, (30, 30, 30), body_end, (58, 80), 4)

        if equipped_pose == 'one_foot':
            pygame.draw.line(scooter_surf, (30, 30, 30), body_end, (15, 58), 4)
        else:
            pygame.draw.line(scooter_surf, (30, 30, 30), body_end, (32, 80), 4)

        # Поворот
        rotated_scooter = pygame.transform.rotate(scooter_surf, game_state['angle'])

        orig_center = pygame.math.Vector2(sc_w / 2, sc_h / 2)
        pivot_vector = pygame.math.Vector2(pivot_x, pivot_y) - orig_center
        pivot_vector.rotate_ip(-game_state['angle'])

        new_center = (rear_wheel_x, ground_y) - pivot_vector
        rect = rotated_scooter.get_rect(center=(int(new_center.x), int(new_center.y)))
        virtual_screen.blit(rotated_scooter, rect.topleft)

        # Кнопки управления
        pygame.draw.rect(virtual_screen, (255, 140, 0), btn_stunt, border_radius=14)
        pygame.draw.rect(virtual_screen, (220, 20, 60), btn_brake, border_radius=14)

        stunt_txt = font_btn_med.render("СТАНТ", True, (255, 255, 255))
        brake_txt = font_btn_med.render("ТОРМОЗ", True, (255, 255, 255))
        virtual_screen.blit(stunt_txt, stunt_txt.get_rect(center=btn_stunt.center))
        virtual_screen.blit(brake_txt, brake_txt.get_rect(center=btn_brake.center))

        # Интерфейс
        score_txt = font_large.render(f"Очки: {game_state['score']}", True, (0, 0, 0))
        coins_hud = font_btn_med.render(f"Всего монет: {total_coins}", True, (0, 100, 0))
        virtual_screen.blit(score_txt, (15, 15))
        virtual_screen.blit(coins_hud, (15, 45))

        btn_home = pygame.Rect(V_WIDTH - 50, 15, 35, 30)
        pygame.draw.rect(virtual_screen, (100, 100, 100), btn_home, border_radius=8)
        home_txt = font_btn_med.render("X", True, (255, 255, 255))
        virtual_screen.blit(home_txt, home_txt.get_rect(center=btn_home.center))

        if mouse_click and btn_home.collidepoint(mx, my):
            current_state = 'menu'

        # Текст трюков
        if game_state['is_stunting'] and not game_state['game_over']:
            if equipped_pose == 'one_foot':
                status_txt = font_large.render("ONE FOOT! +4", True, (180, 50, 230))
            elif equipped_pose == 'no_hand':
                status_txt = font_large.render("NO HAND! +6", True, (255, 140, 0))
            else:
                status_txt = font_large.render("MANUAL! +2", True, (0, 150, 255))

            virtual_screen.blit(status_txt, (V_WIDTH // 2 - status_txt.get_width() // 2, 75))

        # Экран падения
        if game_state['game_over']:
            overlay = pygame.Surface((V_WIDTH, V_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            virtual_screen.blit(overlay, (0, 0))

            over_txt = font_title.render("УПАЛ!", True, (255, 50, 50))
            virtual_screen.blit(over_txt, (V_WIDTH // 2 - over_txt.get_width() // 2, 190))

            res_coins = font_large.render(f"+{game_state['score']} Монет!", True, (255, 215, 0))
            virtual_screen.blit(res_coins, (V_WIDTH // 2 - res_coins.get_width() // 2, 235))

            pygame.draw.rect(virtual_screen, (0, 200, 80), btn_restart, border_radius=12)
            restart_txt = font_btn_med.render("РЕСПАВН", True, (255, 255, 255))
            virtual_screen.blit(restart_txt, restart_txt.get_rect(center=btn_restart.center))

    # Отображение
    scaled_surface = pygame.transform.scale(virtual_screen, (real_w, real_h))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
