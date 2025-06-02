-- 建立使用者資料表
create table users (
    id uuid primary key default gen_random_uuid (),
    email text unique not null,
    password_hash text not null,
    created_at timestamp
    with
        time zone default now()
);

-- 使用者課堂偏好（課程時間格設定）
create table preferences (
    user_id uuid references users(id) on delete cascade,
    slots text[],
    updated_at timestamp with time zone default now(),
    primary key (user_id)
);

-- 聊天記錄
create table chat_history (
    id bigserial primary key,
    user_id uuid references users(id) on delete cascade,
    user_input text,
    bot_reply text,
    timestamp timestamp with time zone default now(),
    used_slots text[]
);