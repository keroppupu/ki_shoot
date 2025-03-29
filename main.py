import pyxel
import random
import math

class App:
    def __init__(self):
        pyxel.init(160, 120)
        pyxel.load("my_resource.pyxres")

        self.player_x = 20
        self.player_y = 60
        self.player_speed = 2
        self.player_width = 16
        self.player_height = 16
        self.player_health = 10

        self.is_invincible = False  # 無敵状態かどうか
        self.invincible_timer = 0  # 無敵タイマー

        self.bullets = []
        self.bullet_speed = 4
        self.bullet_size = 2

        self.enemies = []
        self.enemy_speed = 1
        self.enemy_spawn_interval = 60
        self.enemy_spawn_timer = 0
        self.enemy_width = 16
        self.enemy_height = 16

        # 上下移動する敵関連
        self.wavy_enemies = []
        self.wavy_enemy_spawn_interval = 90
        self.wavy_enemy_spawn_timer = 0
        self.wavy_enemy_width = 16
        self.wavy_enemy_height = 16
        self.wavy_enemy_speed = 0.7
        self.wavy_enemy_amplitude = 2
        self.wavy_enemy_frequency = 0.05

        self.explosions = []

        self.score = 0
        self.game_over = False
        self.star_count = 50
        self.stars = []
        for _ in range(self.star_count):
            self.stars.append({
                "x": random.randint(0, pyxel.width - 1),
                "y": random.randint(0, pyxel.height - 1),
                "speed": random.uniform(0.1, 0.5)
            })

        # ソード関連
        self.sword_active = False
        self.sword_timer = 0
        self.sword_length = 24  # 剣の長さを長くする
        self.sword_color = 13
        self.sword_x = 0
        self.sword_y = 0

        # ボス関連
        self.boss = None
        self.boss_appeared = False
        self.boss_width = 32
        self.boss_height = 32
        self.boss_health = 20
        self.boss_speed = 0.5
        self.boss_bullet_interval = 120
        self.boss_bullet_timer = 0
        self.boss_bullets = []
        self.boss_y_speed = 0.3
        self.boss_y_direction = 1

        self.screen = "title"

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player_x = 20
        self.player_y = 60
        self.player_health = 10
        self.is_invincible = False
        self.invincible_timer = 0
        self.bullets = []
        self.enemies = []
        self.wavy_enemies = []
        self.explosions = []
        self.score = 0
        self.game_over = False
        self.boss = None
        self.boss_appeared = False

    def update(self):
        if self.screen == "title":
            if pyxel.btnp(pyxel.KEY_A):
                self.screen = "game"
                self.reset_game()

        elif self.screen == "game":
            if self.game_over:
                self.screen = "gameover"
                return

            # 無敵タイマーの更新
            if self.is_invincible:
                self.invincible_timer -= 1
                if self.invincible_timer <= 0:
                    self.is_invincible = False

            # プレイヤーの移動
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player_x = max(0, self.player_x - self.player_speed)  # 画面左端に制限
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.player_x = min(pyxel.width - self.player_width, self.player_x + self.player_speed)  # 画面右端に制限
            if pyxel.btn(pyxel.KEY_UP):
                self.player_y = max(0, self.player_y - self.player_speed)  # 画面上端に制限
            if pyxel.btn(pyxel.KEY_DOWN):
                self.player_y = min(pyxel.height - self.player_height, self.player_y + self.player_speed)  # 画面下端に制限

            # 弾の発射
            if pyxel.btnp(pyxel.KEY_X):  # Xキーが押されたら
                self.bullets.append({"x": self.player_x + self.player_width, "y": self.player_y + self.player_height // 2})

            # ソード攻撃
            if pyxel.btnp(pyxel.KEY_Y):
                self.sword_active = True
                self.sword_timer = 5
                self.sword_x = self.player_x + self.player_width // 2
                self.sword_y = self.player_y # 剣のy座標を調整

            # ソードのタイマー更新とアニメーション
            if self.sword_active:
                self.sword_timer -= 1
                self.sword_x += 5 # 剣の速度を調整
                #self.sword_y += 2 # 剣の速度を調整

                if self.sword_timer <= 0:
                    self.sword_active = False

            # 弾の移動
            for bullet in self.bullets:
                bullet["x"] += self.bullet_speed

            # 敵の生成
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer > self.enemy_spawn_interval:
                self.enemies.append({
                    "x": pyxel.width,
                    "y": random.randint(0, pyxel.height - self.enemy_height),
                    "health": 2,
                    "type": "normal"
                })
                self.enemy_spawn_timer = 0

            # 上下移動する敵の生成
            self.wavy_enemy_spawn_timer += 1
            if self.wavy_enemy_spawn_timer > self.wavy_enemy_spawn_interval:
                self.wavy_enemies.append({
                    "x": pyxel.width,
                    "y": random.randint(0, pyxel.height - self.wavy_enemy_height),
                    "health": 1,
                    "offset": random.uniform(0, 2 * math.pi),
                })
                self.wavy_enemy_spawn_timer = 0

            # ボスの出現
            if self.score > 100 and not self.boss_appeared:
                self.boss = {
                    "x": pyxel.width,
                    "y": pyxel.height // 2 - self.boss_height // 2,
                    "health": self.boss_health
                }
                self.boss_appeared = True

            # 敵の移動
            for enemy in self.enemies:
                enemy["x"] -= self.enemy_speed

            # 上下移動する敵の移動
            for enemy in self.wavy_enemies:
                enemy["x"] -= self.wavy_enemy_speed
                enemy["y"] += self.wavy_enemy_amplitude * math.sin(enemy["offset"] + pyxel.frame_count * self.wavy_enemy_frequency)

            # ボスの移動
            if self.boss:
                new_boss_x = self.boss["x"] - self.boss_speed

                if new_boss_x > pyxel.width // 2:
                    self.boss["x"] = new_boss_x
                else:
                    self.boss["x"] = pyxel.width // 2

                self.boss["y"] += self.boss_y_speed * self.boss_y_direction

                if self.boss["y"] < 0 or self.boss["y"] > pyxel.height - self.boss_height:
                    self.boss_y_direction *= -1

            # ボスの弾の発射
            if self.boss:
                self.boss_bullet_timer += 1
                if self.boss_bullet_timer > self.boss_bullet_interval:
                    self.boss_bullets.append({
                        "x": self.boss["x"],
                        "y": self.boss["y"] + self.boss_height // 2,
                        "speed_x": -1.5,
                        "speed_y": random.uniform(-0.5, 0.5),
                        "size": 3
                    })
                    self.boss_bullet_timer = 0

            # ボスの弾の移動
            for bullet in self.boss_bullets:
                bullet["x"] += bullet["speed_x"]
                bullet["y"] += bullet["speed_y"]

            # ---------------------- 当たり判定 ----------------------

            # 弾 vs 敵
            for bullet in list(self.bullets):
                for enemy in list(self.enemies):
                    if (bullet["x"] < enemy["x"] + self.enemy_width and
                        bullet["x"] + self.bullet_size > enemy["x"] and
                        bullet["y"] < enemy["y"] + self.enemy_height and
                        bullet["y"] + self.bullet_size > enemy["y"]):
                        self.bullets.remove(bullet)
                        enemy["x"] += 2
                        enemy["health"] -= 1
                        if enemy["health"] <= 0:
                            # 爆発エフェクトの生成
                            for _ in range(8):  # 爆発のパーティクルの数
                                angle = random.uniform(0, 2 * math.pi)  # ランダムな角度
                                speed = random.uniform(1, 3)  # ランダムな速度
                                vx = math.cos(angle) * speed  # X方向の速度
                                vy = math.sin(angle) * speed  # Y方向の速度
                                size = random.randint(1, 3)  # ランダムなサイズ
                                color = random.choice([10, 11, 12])  # ランダムな色
                                self.explosions.append({
                                    "x": enemy["x"] + self.enemy_width // 2,  # 敵の中心
                                    "y": enemy["y"] + self.enemy_height // 2,  # 敵の中心
                                    "vx": vx,
                                    "vy": vy,
                                    "size": size,
                                    "color": color,
                                    "timer": 10  # 寿命
                                })
                            self.enemies.remove(enemy)
                            self.score += 10
                        break

            # 弾 vs 上下移動する敵
            for bullet in list(self.bullets):
                for enemy in list(self.wavy_enemies):
                    if (bullet["x"] < enemy["x"] + self.wavy_enemy_width and
                        bullet["x"] + self.bullet_size > enemy["x"] and
                        bullet["y"] < enemy["y"] + self.wavy_enemy_height and
                        bullet["y"] + self.bullet_size > enemy["y"]):
                        self.bullets.remove(bullet)
                        enemy["x"] += 2 # 敵を少しノックバックさせる
                        enemy["health"] -= 1
                        if enemy["health"] <= 0:
                            # 爆発エフェクトの生成
                            for _ in range(8):  # 爆発のパーティクルの数
                                angle = random.uniform(0, 2 * math.pi)  # ランダムな角度
                                speed = random.uniform(1, 3)  # ランダムな速度
                                vx = math.cos(angle) * speed  # X方向の速度
                                vy = math.sin(angle) * speed  # Y方向の速度
                                size = random.randint(1, 3)  # ランダムなサイズ
                                color = random.choice([10, 11, 12])  # ランダムな色
                                self.explosions.append({
                                    "x": enemy["x"] + self.wavy_enemy_width // 2,  # 敵の中心
                                    "y": enemy["y"] + self.wavy_enemy_height // 2,  # 敵の中心
                                    "vx": vx,
                                    "vy": vy,
                                    "size": size,
                                    "color": color,
                                    "timer": 10  # 寿命
                                })
                            self.wavy_enemies.remove(enemy)
                            self.score += 10
                        break

            # 弾 vs ボス
            if self.boss:
                for bullet in list(self.bullets):
                    if (bullet["x"] < self.boss["x"] + self.boss_width and
                        bullet["x"] + self.bullet_size > self.boss["x"] and
                        bullet["y"] < self.boss["y"] + self.boss_height and
                        bullet["y"] + self.bullet_size > self.boss["y"]):
                        self.bullets.remove(bullet)
                        self.boss["health"] -= 1
                        if self.boss["health"] <= 0:
                            # 爆発エフェクトの生成
                            for _ in range(16):  # 爆発のパーティクルの数
                                angle = random.uniform(0, 2 * math.pi)  # ランダムな角度
                                speed = random.uniform(1, 3)  # ランダムな速度
                                vx = math.cos(angle) * speed  # X方向の速度
                                vy = math.sin(angle) * speed  # Y方向の速度
                                size = random.randint(2, 4)  # ランダムなサイズ
                                color = random.choice([10, 11, 12])  # ランダムな色
                                self.explosions.append({
                                    "x": self.boss["x"] + self.boss_width // 2,  # ボスの中心
                                    "y": self.boss["y"] + self.boss_height // 2,  # ボスの中心
                                    "vx": vx,
                                    "vy": vy,
                                    "size": size,
                                    "color": color,
                                    "timer": 10  # 寿命
                                })
                            self.boss = None
                            self.boss_appeared = False
                            self.score += 50
                        break

            # プレイヤー vs 敵
            for enemy in list(self.enemies):
                if (not self.is_invincible and  # 無敵状態ではない場合のみ当たり判定
                    self.player_x < enemy["x"] + self.enemy_width and
                    self.player_x + self.player_width > enemy["x"] and
                    self.player_y < enemy["y"] + self.enemy_height and
                    self.player_y + self.player_height > enemy["y"]):
                    self.player_health -= 1
                    if self.player_health <= 0:
                        self.game_over = True
                        break

                    # ノックバック処理 (画面外に出ないように制限)
                    if self.player_x < enemy["x"]:  # プレイヤーが敵の左側にいる場合
                        knockback_x = -5
                        self.player_x = max(0, self.player_x + knockback_x) # 左端から出ないように制限
                    else:  # プレイヤーが敵の右側にいる場合
                        knockback_x = 5
                        self.player_x = min(pyxel.width - self.player_width, self.player_x + knockback_x)  # 右端から出ないように制限

                    enemy["x"] += 5 if enemy["x"] < self.player_x else -5

                    # 無敵状態にする
                    self.is_invincible = True
                    self.invincible_timer = 60  # 無敵時間 (60フレーム = 1秒)

            # プレイヤー vs 上下移動する敵
            for enemy in list(self.wavy_enemies):
                if (not self.is_invincible and  # 無敵状態ではない場合のみ当たり判定
                    self.player_x < enemy["x"] + self.wavy_enemy_width and
                    self.player_x + self.player_width > enemy["x"] and
                    self.player_y < enemy["y"] + self.wavy_enemy_height and
                    self.player_y + self.player_height > enemy["y"]):
                    self.player_health -= 1
                    if self.player_health <= 0:
                        self.game_over = True
                        break

                    # ノックバック処理 (画面外に出ないように制限)
                    if self.player_x < enemy["x"]:  # プレイヤーが敵の左側にいる場合
                        knockback_x = -5
                        self.player_x = max(0, self.player_x + knockback_x)  # 左端から出ないように制限
                    else:  # プレイヤーが敵の右側にいる場合
                        knockback_x = 5
                        self.player_x = min(pyxel.width - self.player_width, self.player_x + knockback_x)  # 右端から出ないように制限

                    enemy["x"] += 5 if enemy["x"] < self.player_x else -5

                    # 無敵状態にする
                    self.is_invincible = True
                    self.invincible_timer = 60  # 無敵時間 (60フレーム = 1秒)

            # プレイヤー vs ボスの弾
            for bullet in list(self.boss_bullets):
                if (not self.is_invincible and # 無敵状態ではない場合のみ当たり判定
                    self.player_x < bullet["x"] + bullet["size"] and
                    self.player_x + self.player_width > bullet["x"] and
                    self.player_y < bullet["y"] + bullet["size"] and
                    self.player_y + self.player_height > bullet["y"]):
                    self.boss_bullets.remove(bullet)
                    self.player_health -= 1
                    if self.player_health <= 0:
                        self.game_over = True
                        break

                    # 無敵状態にする
                    self.is_invincible = True
                    self.invincible_timer = 60 # 無敵時間(60フレーム = 1秒)

            # ソード vs 敵
            if self.sword_active:
                sword_x_end = self.sword_x + self.sword_length
                for enemy in list(self.enemies):
                    if (self.sword_x < enemy["x"] + self.enemy_width and
                        sword_x_end > enemy["x"] and
                        self.sword_y < enemy["y"] + self.enemy_height and
                        self.sword_y + 1 > enemy["y"]):
                        # 爆発エフェクトの生成
                        for _ in range(8):  # 爆発のパーティクルの数
                            angle = random.uniform(0, 2 * math.pi)  # ランダムな角度
                            speed = random.uniform(1, 3)  # ランダムな速度
                            vx = math.cos(angle) * speed  # X方向の速度
                            vy = math.sin(angle) * speed  # Y方向の速度
                            size = random.randint(1, 3)  # ランダムなサイズ
                            color = random.choice([10, 11, 12])  # ランダムな色
                            self.explosions.append({
                                "x": enemy["x"] + self.enemy_width // 2,  # 敵の中心
                                "y": enemy["y"] + self.enemy_height // 2,  # 敵の中心
                                "vx": vx,
                                "vy": vy,
                                "size": size,
                                "color": color,
                                "timer": 10  # 寿命
                            })
                        self.enemies.remove(enemy)
                        self.score += 10  # スコアを加算
                        break

            # ソード vs 上下移動する敵
            if self.sword_active:
                sword_x_end = self.sword_x + self.sword_length
                for enemy in list(self.wavy_enemies):
                    if (self.sword_x < enemy["x"] + self.wavy_enemy_width and
                        sword_x_end > enemy["x"] and
                        self.sword_y < enemy["y"] + self.wavy_enemy_height and
                        self.sword_y + 1 > enemy["y"]):
                        # 爆発エフェクトの生成
                        for _ in range(8):  # 爆発のパーティクルの数
                            angle = random.uniform(0, 2 * math.pi)  # ランダムな角度
                            speed = random.uniform(1, 3)  # ランダムな速度
                            vx = math.cos(angle) * speed  # X方向の速度
                            vy = math.sin(angle) * speed  # Y方向の速度
                            size = random.randint(1, 3)  # ランダムなサイズ
                            color = random.choice([10, 11, 12])  # ランダムな色
                            self.explosions.append({
                                "x": enemy["x"] + self.wavy_enemy_width // 2,  # 敵の中心
                                "y": enemy["y"] + self.wavy_enemy_height // 2,  # 敵の中心
                                "vx": vx,
                                "vy": vy,
                                "size": size,
                                "color": color,
                                "timer": 10  # 寿命
                            })
                        self.wavy_enemies.remove(enemy)
                        self.score += 10
                        break

            # ---------------------- 当たり判定ここまで ----------------------

            # 画面外に出た弾を削除
            self.bullets = [bullet for bullet in self.bullets if bullet["x"] < pyxel.width]
            # 画面外に出た敵を削除
            self.enemies = [enemy for enemy in self.enemies if enemy["x"] > -self.enemy_width]
            # 画面外に出た上下移動する敵を削除
            self.wavy_enemies = [enemy for enemy in self.wavy_enemies if enemy["x"] > -self.wavy_enemy_width]
            # 画面外に出たボスの弾を削除
            self.boss_bullets = [bullet for bullet in self.boss_bullets if bullet["x"] > -5 and bullet["x"] < pyxel.width and bullet["y"] > -5 and bullet["y"] < pyxel.height]

            # 星の移動
            for star in self.stars:
                star["x"] -= star["speed"]
                if star["x"] < 0:
                    star["x"] = pyxel.width
                    star["y"] = random.randint(0, pyxel.height - 1)

            # 爆発エフェクトの更新
            for explosion in list(self.explosions):
                explosion["x"] += explosion["vx"]
                explosion["y"] += explosion["vy"]
                explosion["timer"] -= 1
                if explosion["timer"] <= 0:
                    self.explosions.remove(explosion)

        elif self.screen == "gameover":
            if pyxel.btnp(pyxel.KEY_A):
                self.screen = "title"

    def draw(self):
        if self.screen == "title":
            pyxel.cls(0)
            pyxel.text(pyxel.width // 2 - 20, pyxel.height // 2 - 5, "シューティングゲーム", 7)
            pyxel.text(pyxel.width // 2 - 30, pyxel.height // 2 + 5, "SPACEキーでスタート", 7)

        elif self.screen == "game":
            pyxel.cls(0)

            # 星を描画
            for star in self.stars:
                pyxel.pset(int(star["x"]), int(star["y"]), 7)

            # プレイヤーの描画
            if self.is_invincible and pyxel.frame_count % 10 < 5:  # 無敵状態なら点滅
                pass  # 描画しない
            else:
                pyxel.blt(self.player_x, self.player_y, 0, 0, 0, self.player_width, self.player_height, 0)

            # ソードの描画
            if self.sword_active:
                pyxel.rect(int(self.sword_x), int(self.sword_y), self.sword_length, 1, self.sword_color)

            # 弾の描画
            for bullet in self.bullets:
                pyxel.rect(bullet["x"], bullet["y"], self.bullet_size, self.bullet_size, 10)

            # 敵の描画
            for enemy in self.enemies:
                pyxel.blt(enemy["x"], enemy["y"], 0, 16, 0, self.enemy_width, self.enemy_height, 0)

            # 上下移動する敵の描画 (省略)
            for enemy in self.wavy_enemies:
                pyxel.blt(int(enemy["x"]), int(enemy["y"]), 0, 32, 0, self.wavy_enemy_width, self.wavy_enemy_height, 0)

            # ボスの描画
            if self.boss:
                pyxel.blt(int(self.boss["x"]), int(self.boss["y"]), 0, 0, 16, self.boss_width, self.boss_height, 0)

            # ボスの弾の描画
            for bullet in self.boss_bullets:
                pyxel.rect(int(bullet["x"]), int(bullet["y"]), bullet["size"], bullet["size"], 9)

            # 爆発エフェクトの描画
            for explosion in self.explosions:
                pyxel.rect(int(explosion["x"]), int(explosion["y"]), explosion["size"], explosion["size"], explosion["color"])

            # スコアの表示
            pyxel.text(5, 5, f"SCORE: {self.score}", 7)

            # 体力ゲージの表示
            pyxel.text(5, 15, f"HP: {self.player_health}", 7)

        elif self.screen == "gameover":
            pyxel.cls(0)
            pyxel.text(pyxel.width // 2 - 25, pyxel.height // 2 - 5, "GAME OVER", 8)
            pyxel.text(pyxel.width // 2 - 30, pyxel.height // 2 + 5, f"SCORE: {self.score}", 7)
            pyxel.text(pyxel.width // 2 - 30, pyxel.height // 2 + 15, "SPACEキーでタイトル", 7)

App()