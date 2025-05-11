use piston_window::*;
use std::collections::LinkedList;
use std::time::{Instant, Duration};

// Настройки игры
const WIDTH: u32 = 600;
const HEIGHT: u32 = 600;
const GRID_SIZE: u32 = 20;
const GRID_WIDTH: u32 = WIDTH / GRID_SIZE;
const GRID_HEIGHT: u32 = HEIGHT / GRID_SIZE;
const INITIAL_SPEED: f64 = 8.0;

// Цвета
const SNAKE_COLOR: [f32; 4] = [0.0, 1.0, 0.0, 1.0];
const FOOD_COLOR: [f32; 4] = [1.0, 0.0, 0.0, 1.0];
const BG_COLOR: [f32; 4] = [0.1, 0.1, 0.1, 1.0];
const TEXT_COLOR: [f32; 4] = [1.0, 1.0, 1.0, 1.0];
const MENU_COLOR: [f32; 4] = [0.2, 0.2, 0.2, 0.8];

// Направления
#[derive(Clone, Copy, PartialEq)]
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

impl Direction {
    fn opposite(&self) -> Direction {
        match *self {
            Direction::Up => Direction::Down,
            Direction::Down => Direction::Up,
            Direction::Left => Direction::Right,
            Direction::Right => Direction::Left,
        }
    }
}

// Позиция на сетке
#[derive(Clone, Copy, PartialEq)]
struct Position {
    x: u32,
    y: u32,
}

impl Position {
    fn new(x: u32, y: u32) -> Self {
        Position { x, y }
    }
}

// Состояние игры
enum GameState {
    Menu,
    Playing,
    GameOver,
}

// Счётчик FPS
struct FPSCounter {
    last_second: Instant,
    frame_count: u32,
    current_fps: f32,
}

impl FPSCounter {
    fn new() -> Self {
        FPSCounter {
            last_second: Instant::now(),
            frame_count: 0,
            current_fps: 0.0,
        }
    }

    fn tick(&mut self) -> f32 {
        self.frame_count += 1;
        let elapsed = self.last_second.elapsed();
        if elapsed >= Duration::from_secs(1) {
            self.current_fps = self.frame_count as f32 / elapsed.as_secs_f32();
            self.frame_count = 0;
            self.last_second = Instant::now();
        }
        self.current_fps
    }
}

// Игровые данные
struct Game {
    snake: LinkedList<Position>,
    direction: Direction,
    next_direction: Direction,
    food: Position,
    score: u32,
    speed: f64,
    last_update: Instant,
    state: GameState,
    fps_counter: FPSCounter,
    high_score: u32,
}

impl Game {
    fn new() -> Self {
        let mut snake = LinkedList::new();
        snake.push_back(Position::new(GRID_WIDTH / 2, GRID_HEIGHT / 2));

        Game {
            snake,
            direction: Direction::Right,
            next_direction: Direction::Right,
            food: Position::new(0, 0),
            score: 0,
            speed: INITIAL_SPEED,
            last_update: Instant::now(),
            state: GameState::Menu,
            fps_counter: FPSCounter::new(),
            high_score: 0,
        }
    }

    fn reset(&mut self) {
        self.snake.clear();
        self.snake.push_back(Position::new(GRID_WIDTH / 2, GRID_HEIGHT / 2));
        self.direction = Direction::Right;
        self.next_direction = Direction::Right;
        self.score = 0;
        self.speed = INITIAL_SPEED;
        self.spawn_food();
        self.last_update = Instant::now();
    }

    fn spawn_food(&mut self) {
        use rand::Rng;
        let mut rng = rand::thread_rng();

        loop {
            let x = rng.gen_range(0..GRID_WIDTH);
            let y = rng.gen_range(0..GRID_HEIGHT);
            let pos = Position::new(x, y);

            if !self.snake.contains(&pos) {
                self.food = pos;
                break;
            }
        }
    }

    fn update(&mut self) {
        if let GameState::Playing = self.state {
            let now = Instant::now();
            let elapsed = now - self.last_update;
            let update_interval = Duration::from_secs_f64(1.0 / self.speed);

            if elapsed >= update_interval {
                self.direction = self.next_direction;

                // Получаем текущую позицию головы
                let head = *self.snake.front().unwrap();
                let new_head = match self.direction {
                    Direction::Up => Position::new(head.x, (head.y + GRID_HEIGHT - 1) % GRID_HEIGHT),
                    Direction::Down => Position::new(head.x, (head.y + 1) % GRID_HEIGHT),
                    Direction::Left => Position::new((head.x + GRID_WIDTH - 1) % GRID_WIDTH, head.y),
                    Direction::Right => Position::new((head.x + 1) % GRID_WIDTH, head.y),
                };

                // Проверяем столкновение с собой
                if self.snake.contains(&new_head) {
                    self.state = GameState::GameOver;
                    if self.score > self.high_score {
                        self.high_score = self.score;
                    }
                    return;
                }

                // Добавляем новую голову
                self.snake.push_front(new_head);

                // Проверяем, съели ли еду
                if new_head == self.food {
                    self.score += 1;
                    self.speed += 0.5; // Увеличиваем скорость
                    self.spawn_food();
                } else {
                    // Удаляем хвост, если не съели еду
                    self.snake.pop_back();
                }

                self.last_update = now;
            }
        }
    }

    fn handle_input(&mut self, button: Button) {
        match button {
            Button::Keyboard(key) => {
                match self.state {
                    GameState::Menu | GameState::GameOver => {
                        if key == Key::Return {
                            self.state = GameState::Playing;
                            self.reset();
                        }
                    }
                    GameState::Playing => {
                        let new_dir = match key {
                            Key::Up => Direction::Up,
                            Key::Down => Direction::Down,
                            Key::Left => Direction::Left,
                            Key::Right => Direction::Right,
                            _ => return,
                        };

                        // Не позволяем змейке развернуться на 180 градусов
                        if new_dir != self.direction.opposite() {
                            self.next_direction = new_dir;
                        }
                    }
                }
            }
            _ => {}
        }
    }

    fn draw(&mut self, c: Context, g: &mut G2d, glyphs: &mut Glyphs) {
        // Очищаем экран
        clear(BG_COLOR, g);

        match self.state {
            GameState::Menu => self.draw_menu(c, g, glyphs),
            GameState::Playing => {
                self.draw_game(c, g);
                self.draw_hud(c, g, glyphs);
            }
            GameState::GameOver => {
                self.draw_game(c, g);
                self.draw_hud(c, g, glyphs);
                self.draw_game_over(c, g, glyphs);
            }
        }
    }

    fn draw_game(&self, c: Context, g: &mut G2d) {
        // Рисуем еду
        rectangle(
            FOOD_COLOR,
            [
                self.food.x as f64 * GRID_SIZE as f64,
                self.food.y as f64 * GRID_SIZE as f64,
                GRID_SIZE as f64,
                GRID_SIZE as f64,
            ],
            c.transform,
            g,
        );

        // Рисуем змейку
        for pos in &self.snake {
            rectangle(
                SNAKE_COLOR,
                [
                    pos.x as f64 * GRID_SIZE as f64,
                    pos.y as f64 * GRID_SIZE as f64,
                    GRID_SIZE as f64,
                    GRID_SIZE as f64,
                ],
                c.transform,
                g,
            );
        }
    }

    fn draw_hud(&mut self, c: Context, g: &mut G2d, glyphs: &mut Glyphs) {
        // Отображаем счёт
        let score_text = format!("Score: {}", self.score);
        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                &score_text,
                glyphs,
                &c.draw_state,
                c.transform.trans(10.0, 30.0),
                g,
            )
            .unwrap();

        // Отображаем FPS
        let fps = self.fps_counter.tick();
        let fps_text = format!("FPS: {:.0}", fps);
        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                &fps_text,
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 - 100.0, 30.0),
                g,
            )
            .unwrap();
    }

    fn draw_menu(&self, c: Context, g: &mut G2d, glyphs: &mut Glyphs) {
        // Полупрозрачный фон меню
        rectangle(
            MENU_COLOR,
            [100.0, 150.0, WIDTH as f64 - 200.0, HEIGHT as f64 - 300.0],
            c.transform,
            g,
        );

        // Заголовок
        text::Text::new_color(TEXT_COLOR, 40)
            .draw(
                "Snake Game",
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 100.0, 200.0),
                g,
            )
            .unwrap();

        // Инструкции
        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                "Use arrow keys to control",
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 120.0, 300.0),
                g,
            )
            .unwrap();

        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                "Press Enter to start",
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 90.0, 350.0),
                g,
            )
            .unwrap();

        // Рекорд
        let high_score_text = format!("High Score: {}", self.high_score);
        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                &high_score_text,
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 70.0, 400.0),
                g,
            )
            .unwrap();
    }

    fn draw_game_over(&self, c: Context, g: &mut G2d, glyphs: &mut Glyphs) {
        // Полупрозрачный фон
        rectangle(
            MENU_COLOR,
            [100.0, 200.0, WIDTH as f64 - 200.0, 200.0],
            c.transform,
            g,
        );

        // Текст Game Over
        text::Text::new_color(TEXT_COLOR, 30)
            .draw(
                "Game Over",
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 70.0, 250.0),
                g,
            )
            .unwrap();

        // Финальный счёт
        let score_text = format!("Score: {}", self.score);
        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                &score_text,
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 40.0, 300.0),
                g,
            )
            .unwrap();

        // Инструкция
        text::Text::new_color(TEXT_COLOR, 20)
            .draw(
                "Press Enter to restart",
                glyphs,
                &c.draw_state,
                c.transform.trans(WIDTH as f64 / 2.0 - 90.0, 350.0),
                g,
            )
            .unwrap();
    }
}

fn main() {
    let mut window: PistonWindow = WindowSettings::new("Snake", [WIDTH, HEIGHT])
        .exit_on_esc(true)
        .build()
        .unwrap();

    let mut game = Game::new();
    game.spawn_food();

    let mut glyphs = window.load_font("assets/LibreBaskerville-Italic.ttf").unwrap_or_else(|e| {
        panic!("Failed to load font: {}", e);
    });

    while let Some(e) = window.next() {
        // Обработка ввода
        if let Some(Button::Keyboard(key)) = e.press_args() {
            game.handle_input(Button::Keyboard(key));
        }

        // Обновление игры
        if let Some(_) = e.update_args() {
            game.update();
        }

        // Отрисовка
        window.draw_2d(&e, |c, g, device| {
            game.draw(c, g, &mut glyphs);
            glyphs.factory.encoder.flush(device);
        });
    }
}