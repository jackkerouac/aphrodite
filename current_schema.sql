--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Debian 14.17-1.pgdg120+1)
-- Dumped by pg_dump version 14.17 (Debian 14.17-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_modified_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: jellyfin_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jellyfin_settings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    jellyfin_url character varying(255) NOT NULL,
    jellyfin_api_key character varying(255) NOT NULL,
    jellyfin_user_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: jellyfin_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.jellyfin_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: jellyfin_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.jellyfin_settings_id_seq OWNED BY public.jellyfin_settings.id;


--
-- Name: omdb_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.omdb_settings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    api_key character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: omdb_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.omdb_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: omdb_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.omdb_settings_id_seq OWNED BY public.omdb_settings.id;


--
-- Name: tmdb_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tmdb_settings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    api_key character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tmdb_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tmdb_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tmdb_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tmdb_settings_id_seq OWNED BY public.tmdb_settings.id;


--
-- Name: tvdb_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tvdb_settings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    api_key character varying(255) NOT NULL,
    pin character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tvdb_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tvdb_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tvdb_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tvdb_settings_id_seq OWNED BY public.tvdb_settings.id;


--
-- Name: user_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_settings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    theme character varying(20) DEFAULT 'light'::character varying,
    language character varying(10) DEFAULT 'en'::character varying,
    notifications_enabled boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_settings_id_seq OWNED BY public.user_settings.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: jellyfin_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jellyfin_settings ALTER COLUMN id SET DEFAULT nextval('public.jellyfin_settings_id_seq'::regclass);


--
-- Name: omdb_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.omdb_settings ALTER COLUMN id SET DEFAULT nextval('public.omdb_settings_id_seq'::regclass);


--
-- Name: tmdb_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tmdb_settings ALTER COLUMN id SET DEFAULT nextval('public.tmdb_settings_id_seq'::regclass);


--
-- Name: tvdb_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tvdb_settings ALTER COLUMN id SET DEFAULT nextval('public.tvdb_settings_id_seq'::regclass);


--
-- Name: user_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_settings ALTER COLUMN id SET DEFAULT nextval('public.user_settings_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: jellyfin_settings jellyfin_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jellyfin_settings
    ADD CONSTRAINT jellyfin_settings_pkey PRIMARY KEY (id);


--
-- Name: jellyfin_settings jellyfin_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jellyfin_settings
    ADD CONSTRAINT jellyfin_settings_user_id_key UNIQUE (user_id);


--
-- Name: omdb_settings omdb_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.omdb_settings
    ADD CONSTRAINT omdb_settings_pkey PRIMARY KEY (id);


--
-- Name: omdb_settings omdb_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.omdb_settings
    ADD CONSTRAINT omdb_settings_user_id_key UNIQUE (user_id);


--
-- Name: tmdb_settings tmdb_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tmdb_settings
    ADD CONSTRAINT tmdb_settings_pkey PRIMARY KEY (id);


--
-- Name: tmdb_settings tmdb_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tmdb_settings
    ADD CONSTRAINT tmdb_settings_user_id_key UNIQUE (user_id);


--
-- Name: tvdb_settings tvdb_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tvdb_settings
    ADD CONSTRAINT tvdb_settings_pkey PRIMARY KEY (id);


--
-- Name: tvdb_settings tvdb_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tvdb_settings
    ADD CONSTRAINT tvdb_settings_user_id_key UNIQUE (user_id);


--
-- Name: user_settings user_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT user_settings_pkey PRIMARY KEY (id);


--
-- Name: user_settings user_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT user_settings_user_id_key UNIQUE (user_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: jellyfin_settings update_jellyfin_settings_modtime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_jellyfin_settings_modtime BEFORE UPDATE ON public.jellyfin_settings FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: omdb_settings update_omdb_settings_modtime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_omdb_settings_modtime BEFORE UPDATE ON public.omdb_settings FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: tmdb_settings update_tmdb_settings_modtime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_tmdb_settings_modtime BEFORE UPDATE ON public.tmdb_settings FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: tvdb_settings update_tvdb_settings_modtime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_tvdb_settings_modtime BEFORE UPDATE ON public.tvdb_settings FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: user_settings update_user_settings_modtime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_user_settings_modtime BEFORE UPDATE ON public.user_settings FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: users update_users_modtime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_users_modtime BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- Name: jellyfin_settings jellyfin_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jellyfin_settings
    ADD CONSTRAINT jellyfin_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: omdb_settings omdb_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.omdb_settings
    ADD CONSTRAINT omdb_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tmdb_settings tmdb_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tmdb_settings
    ADD CONSTRAINT tmdb_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tvdb_settings tvdb_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tvdb_settings
    ADD CONSTRAINT tvdb_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_settings user_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT user_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

