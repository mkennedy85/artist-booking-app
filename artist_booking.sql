--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

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
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: michaelkennedy
--

COPY public.alembic_version (version_num) FROM stdin;
118971a23114
\.


--
-- Data for Name: artist; Type: TABLE DATA; Schema: public; Owner: michaelkennedy
--

COPY public.artist (id, name, city, state, phone, genres, image_link, facebook_link, website, seeking_venue, seeking_description) FROM stdin;
1	Guns N Petals	San Francisco	CA	326-123-5000	Rock n Roll	https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80	https://www.facebook.com/GunsNPetals	https://www.gunsnpetalsband.com	t	Looking for shows to perform at in the San Francisco Bay Area!
2	Matt Quevedo	New York	NY	300-400-5000	Jazz	https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80	https://www.facebook.com/mattquevedo923251523		f	
3	The Wild Sax Band	San Francisco	CA	432-325-5432	Jazz,Classical	https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80			f	
\.


--
-- Data for Name: venue; Type: TABLE DATA; Schema: public; Owner: michaelkennedy
--

COPY public.venue (id, name, city, state, address, genres, phone, image_link, facebook_link, website, seeking_talent, seeking_description) FROM stdin;
1	The Musical Hop	San Francisco	CA	1015 Folsom Street	Jazz,Reggae,Swing,Classical,Folk	123-123-1234	https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60	https://www.facebook.com/TheMusicalHop	https://www.themusicalhop.com	t	We are on the lookout for a local artist to play every two weeks. Please call us.
2	The Dueling Pianos Bar	New York	NY	335 Delancey Street	Classical,R&B,Hip-Hop	914-003-1132	https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80	https://www.facebook.com/theduelingpianos	https://www.theduelingpianos.com	f	
3	Park Square Live Music & Coffee	San Francisco	CA	34 Whiskey Moore Ave	Rock n Roll,Jazz,Classical,Folk	415-000-1234	https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80	https://www.facebook.com/ParkSquareLiveMusicAndCoffee	https://www.parksquarelivemusicandcoffee.com	f	
\.


--
-- Data for Name: show; Type: TABLE DATA; Schema: public; Owner: michaelkennedy
--

COPY public.show (id, artist_id, venue_id, start_time) FROM stdin;
1	2	1	2019-05-21T21:30:00.000Z
2	1	3	2019-06-15T23:00:00.000Z
3	3	3	2035-04-01T20:00:00.000Z
4	2	3	2035-04-08T20:00:00.000Z
5	1	3	2035-04-15T20:00:00.000Z
\.


--
-- Name: artist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: michaelkennedy
--

SELECT pg_catalog.setval('public.artist_id_seq', 3, true);


--
-- Name: show_id_seq; Type: SEQUENCE SET; Schema: public; Owner: michaelkennedy
--

SELECT pg_catalog.setval('public.show_id_seq', 5, true);


--
-- Name: venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: michaelkennedy
--

SELECT pg_catalog.setval('public.venue_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--

