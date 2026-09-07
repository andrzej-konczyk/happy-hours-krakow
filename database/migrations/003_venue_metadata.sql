alter table public.venues
    add column if not exists website_url text;

alter table public.venues
    add column if not exists maps_url text;

alter table public.venues
    add column if not exists phone text;
