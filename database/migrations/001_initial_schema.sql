create extension if not exists pgcrypto;

create table if not exists public.venues (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    address text not null,
    lat double precision not null,
    lng double precision not null,
    category text not null default 'pub',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.deals (
    id uuid primary key default gen_random_uuid(),
    venue_id uuid not null references public.venues(id) on delete cascade,
    description text not null,
    start_time time not null,
    end_time time not null,
    days_of_week text[] not null,
    type text not null default 'mixed',
    tags text[] not null default '{}',
    value_score integer not null default 1 check (value_score between 1 and 5),
    source_url text,
    source_scraped_at timestamptz,
    confidence text check (confidence in ('high', 'medium', 'low')),
    dedupe_key text not null unique,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists deals_venue_id_idx on public.deals (venue_id);
create index if not exists deals_type_idx on public.deals (type);
create index if not exists deals_days_of_week_idx on public.deals using gin (days_of_week);

alter table public.venues enable row level security;
alter table public.deals enable row level security;

create policy "public can read venues"
    on public.venues for select
    using (true);

create policy "public can read deals"
    on public.deals for select
    using (true);
