alter table public.deals
    add column if not exists status text not null default 'verified'
        check (status in ('pending', 'verified', 'expired'));

alter table public.deals
    add column if not exists verified_at timestamptz;

alter table public.deals
    add column if not exists valid_until date;

create index if not exists deals_status_idx on public.deals (status);
create index if not exists deals_valid_until_idx on public.deals (valid_until);
