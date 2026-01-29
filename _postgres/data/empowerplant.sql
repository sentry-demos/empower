--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.24
-- Dumped by pg_dump version 14.8 (Homebrew)

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
-- Name: backorder_inventory; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.backorder_inventory AS
 SELECT (pg_sleep(((0.2 * (5)::numeric))::double precision))::text AS pg_sleep;


ALTER TABLE public.backorder_inventory OWNER TO postgres;

SET default_tablespace = '';

--
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    id integer NOT NULL,
    sku character varying NOT NULL,
    count integer NOT NULL,
    productid integer
);


ALTER TABLE public.inventory OWNER TO postgres;

--
-- Name: inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventory_id_seq OWNER TO postgres;

--
-- Name: inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_id_seq OWNED BY public.inventory.id;


--
-- Name: product_bundles; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.product_bundles AS
 SELECT (pg_sleep(((0.0625 * ((ARRAY[3, 10, 7, 5, 3])[floor(((random() * (5)::double precision) + (1)::double precision))])::numeric))::double precision))::text AS pg_sleep;


ALTER TABLE public.product_bundles OWNER TO postgres;

--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    descriptionfull text NOT NULL,
    price integer NOT NULL,
    img text NOT NULL,
    imgcropped text NOT NULL
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    productid integer NOT NULL,
    rating integer NOT NULL,
    customerid integer,
    description text,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reviews_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reviews_id_seq OWNER TO postgres;

--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: promo_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.promo_codes (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    percent_discount integer,
    max_dollar_savings integer,
    is_active boolean DEFAULT true,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.promo_codes OWNER TO postgres;

--
-- Name: promo_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.promo_codes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.promo_codes_id_seq OWNER TO postgres;

--
-- Name: promo_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.promo_codes_id_seq OWNED BY public.promo_codes.id;


--
-- Name: weekly_promotions; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.weekly_promotions AS
 SELECT (pg_sleep(((0.25 * ((ARRAY[3, 10, 7, 5, 3])[floor(((random() * (5)::double precision) + (1)::double precision))])::numeric))::double precision))::text AS pg_sleep;


ALTER TABLE public.weekly_promotions OWNER TO postgres;

--
-- Name: inventory id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN id SET DEFAULT nextval('public.inventory_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: promo_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promo_codes ALTER COLUMN id SET DEFAULT nextval('public.promo_codes_id_seq'::regclass);


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory (id, sku, count, productid) FROM stdin;
5	irfpkztydpfeueye	17	\N
6	kxljbwggsrtujclc	25	\N
7	bpiplgewiwnbvqfi	12	\N
8	rztpqcgnltqnjaso	25	\N
9	ygwzoznsauarvomp	6	\N
10	lmgcqxgahidfnejm	5	\N
11	arovnvkuwneujcox	20	\N
12	avouvokblpdttmqi	22	\N
13	heleijzdxthmnsct	16	\N
14	gkvrujhgoxduzswk	23	\N
15	bhxrvasbcnlpijfs	11	\N
16	wfffdlwcmanycxei	2	\N
17	tcohxiksqgaknpnc	19	\N
18	anuoqioixnkkowpa	19	\N
19	wgttbllcaucbojhp	3	\N
20	hykjhcncclptxfjb	16	\N
21	adijabdsruvqkiwe	14	\N
22	lbszeucgyyvwmjmk	18	\N
23	pcnifwlrllpujpzm	20	\N
24	evrfjnedushxmvmv	12	\N
25	vqjwiuqfctzaubri	29	\N
26	mkivcjodswzmoibi	3	\N
27	dxytwglmbajqabwb	3	\N
28	hptviwfmxbssluxp	14	\N
29	updkbakkwoxnhbxj	10	\N
30	bjyvfgjhqsyfborh	27	\N
31	ptoedlygzuukqsjy	18	\N
32	ofinrxljbhhwqzap	8	\N
33	twmayioxugxfmbgq	24	\N
34	niumupgzjzsqrjno	22	\N
35	nxdzpjpddfxsoygr	7	\N
36	upjbpgvxbbdmoqra	6	\N
37	kkqefxnyxjbyefao	20	\N
38	bhuweevachzmskta	11	\N
39	xlezvizjlpoocqvz	25	\N
40	wfwhhejsklvvmbuh	27	\N
41	nkzqlafiafmnrbhw	21	\N
42	orgcisnxnlachmip	16	\N
43	wnushigyudgldtgl	16	\N
44	bkqtjpshztxcdlyw	12	\N
45	vivwllmitpkizrme	12	\N
46	vltmkrcmoegwgfza	9	\N
47	naaqsymjutzchdwy	6	\N
48	aqacrdrmlzyyzeul	26	\N
49	bqgokmpzgudiybvr	8	\N
50	iofcpxziuolhalah	21	\N
51	ikeylnnvehleqsxh	7	\N
52	wqkulatumgfvldzd	17	\N
53	hoklakwjhdxshugx	27	\N
54	cffbrksscedvzipt	5	\N
55	viyspuowupgixacu	23	\N
56	pgejnzgainbfhuos	30	\N
57	jhsaecvetnktffph	5	\N
58	altjtdtmcwniygak	7	\N
59	fccuewmzalukltkc	2	\N
60	nbaambutehmyyvxp	7	\N
61	evpbxygdmsfrxogx	14	\N
62	asqudkthmzpxmisl	4	\N
63	dibbkltouvpbxobx	24	\N
64	ikprbhoomzemlmvo	8	\N
65	tcfcfwxmffxbhsnw	19	\N
66	ygfglxbzwiptoncj	9	\N
67	oudnojdknalaanbl	8	\N
68	tkgnvmegwildfioi	9	\N
69	dtzhkwcivxscojnq	22	\N
70	vvaampnllwyiqwqi	26	\N
71	rfkjkawgyjgsrnjx	16	\N
72	kcgwezietnhikgfw	6	\N
73	ldlgqrmiinizbjua	3	\N
74	xgmqgfmdltecxsyb	21	\N
75	jclaejidrumhuwbt	2	\N
76	vaziboxpxcgrevwq	22	\N
77	mqxgitbsalmoytas	6	\N
78	oxztelegnjagrnvi	11	\N
79	nvuhbztuupkjufgt	5	\N
80	enlsxgqzrzmscuyf	1	\N
81	wkcpqmdrcjkbxzyx	22	\N
82	mykqhgwkhuscewyk	7	\N
83	ausjvjvowubeghox	17	\N
84	icczobbfeqrmepzr	21	\N
85	eocbgszpyysliugj	24	\N
86	ngyyutmxemirdjbx	16	\N
87	hixkrvqgelfjacnt	29	\N
88	ajnwfbfxnoozrxty	17	\N
89	oxrszsjkmuysuppa	28	\N
90	zaszxmbtqydjydxu	4	\N
91	vrxkxyxabastciom	28	\N
92	svxeelfkkrabpojf	11	\N
93	xliyqapactzrdsxx	8	\N
94	hpekcnzzyaitcnvi	19	\N
95	vvotghxhoygeebuz	6	\N
96	vwurhpwlfofwlpoz	23	\N
97	ckmzjaqjqxwpbhxn	20	\N
98	ipglzkvxmfzatioy	16	\N
99	lzfqqskibppeeoah	27	\N
100	hwapecrmnxzvkqcv	20	\N
101	jdpdyjiujchwtnla	11	\N
102	zqmtlwhzqcyuters	28	\N
103	mpqbpztslfqazwzq	12	\N
104	mhitgjkpcbufthto	8	\N
105	bbjyqsqnjjjpmrth	4	\N
106	vspotybxlyfhsawk	2	\N
107	txybgtchurpxpume	7	\N
108	oimmgyurvkqxpzbq	12	\N
109	yuagytoirhhugnil	29	\N
110	rgcfgxkgraexckrj	28	\N
111	wpeewsoshpqyoxiv	10	\N
112	ygewnpiwxjzkbatt	3	\N
113	rislatttoxyzbetf	7	\N
114	fikficjsqwwxfhlc	21	\N
115	lyqqeuvoajssiwhu	9	\N
116	aerilnezsuuurngt	16	\N
117	hirfrnckgccdtwit	4	\N
118	wsjpbwgdgoppeydi	26	\N
119	krrgriznjvtvjxhu	27	\N
120	wpxaulnrbgoeqocu	23	\N
121	llnezgddutmzirnf	9	\N
122	ecpsgkwzqoyedvsp	24	\N
123	dokigqhbnmiguuzv	6	\N
124	zqajvhitwyoiwvdc	27	\N
125	zhldeuptkajgfqcg	16	\N
126	qkvzdmpyxyvdgekj	14	\N
127	lknudoznxsjnfgii	10	\N
128	rwmlvabsbijfgeje	27	\N
129	tiejgjbfjtpfrcae	6	\N
130	nfeddiapskpfpulp	19	\N
131	bpwbjcsdmcwtvfps	3	\N
132	tjgdglrsmyhqjkaj	29	\N
133	bpioalyocbjwkjpw	30	\N
134	mhohwrxfsymgafah	17	\N
135	dnnyrxbbxxbtbjyh	14	\N
136	lhsykvjpbsowadkp	7	\N
2	vkvnmvpnkagfnrkr	1	4
3	wlzfznigebfrharg	1	5
137	cayublfwsrslbgdc	25	\N
138	mnxjkirhuwdvzrik	19	\N
139	mtdzicwwbhbzonxh	12	\N
140	vgsheqkgodfzkzwc	7	\N
141	ljcdubzmgncfwwct	7	\N
142	sziekiofvtznpzac	2	\N
143	fdxgokktxzrsfluh	3	\N
144	mzgjhwuihwiyyoiv	18	\N
145	bgqwvujifropxqgo	12	\N
146	bkhqxxnolpofwosy	2	\N
147	xerwinsxqmdrfytz	15	\N
148	quvujczugejkmhod	2	\N
149	dsgylsdieqlcdyby	26	\N
150	wuyfwihjppxxprow	14	\N
151	thwfstmlplnlmqoj	27	\N
152	edlqwctepadptpsx	11	\N
153	aorgefncbuygazyz	5	\N
154	kexcivjjjuqyimdy	10	\N
155	swtwlvcfsryxyejp	13	\N
156	detajddowpkrmtlz	22	\N
157	kiabjtzmrjjtlkvz	15	\N
158	omjtxmtgjnouwwvz	9	\N
159	rszrlmsrdgersmak	8	\N
160	eubzaepvkjxkzymz	4	\N
161	ssyiapinbmuziavy	13	\N
162	qsiwanfrrmzudhyv	7	\N
163	rylkcbrdruhwcyeq	28	\N
164	sqzpwjlwpsvdkmvv	3	\N
165	iswuklbgvlmuwqbj	9	\N
166	sonqscmuajbvcpnn	11	\N
167	hjwttvpqaxvfsekd	11	\N
168	xkjlxhicexqahwxt	20	\N
169	sgcgjgxkewzyevdj	4	\N
170	phdojdgehheteqky	20	\N
171	ukxvolljzswhwipb	29	\N
172	gdczuxloowbkkhkt	11	\N
173	ttsmbmdxcvyplafq	23	\N
174	jfagdimhysntpstl	19	\N
175	tdmygwiirjxiktvh	25	\N
176	wjpljttrudcagxev	19	\N
177	ymclroesmoixlnzd	5	\N
178	gcubpzcmxkgewwqy	20	\N
179	cjqjcvfssbealiei	22	\N
180	avsllxdyeltrvwim	3	\N
181	vlqbxjpzrfxmfqhw	6	\N
1	asyqtzmrhsabqxri	1	3
4	zkvsixjthreumjut	1	6
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, title, description, descriptionfull, price, img, imgcropped) FROM stdin;
3	Plant Mood	The mood ring for plants.	Plant Mood transforms plant care into an intuitive, visual experience. The smart ceramic pot accommodates plants up to 6 inches in diameter and features a soft-glow LED ring that shifts colors based on real-time soil moisture, light exposure, and temperature readings. Green means thriving, amber signals attention needed, and a gentle red pulse indicates urgent care required. Ideal for beginners and busy professionals who want reliable plant health feedback without checking an app. Works beautifully with tropical foliage like pothos, philodendrons, and peace lilies. Connects via Bluetooth to the Empower Plant app for historical data and care reminders, or operates standalone for a minimalist setup. The understated design blends seamlessly into modern interiors—functional enough for daily use, elegant enough to be a conversation starter.	155	https://storage.googleapis.com/application-monitoring/mood-planter.jpg	https://storage.googleapis.com/application-monitoring/mood-planter-cropped.jpg
4	Botana Voice	Lets plants speak for themselves.	Botana Voice uses advanced biosignal processing to translate your plant's electrical impulses into actual speech. Place the elegant glass dome sensor near any houseplant, and within 48 hours the AI learns your plant's unique bioelectric patterns. It then vocalizes needs like "I'm thirsty," "Too much sun," or "Feeling great today!" through a built-in speaker with adjustable voice personalities. Perfect for plant enthusiasts who want a deeper, more personal connection with their greenery—or anyone who's ever wondered what their fiddle leaf fig is thinking. Works with most indoor species; best results with expressive plants like calatheas, ferns, and orchids that respond dramatically to environmental changes. Integrates with Alexa, Google Home, and Apple HomeKit to announce plant status or trigger smart home automations. Note: Requires 2-3 weeks of calibration for accurate readings. A true showpiece that will absolutely wow your guests.	175	https://storage.googleapis.com/application-monitoring/plant-to-text.jpg	https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg
5	Plant Stroller	Because plant don't have feet.	Plant Stroller is an autonomous robotic platform that physically moves your potted plant to optimal lighting conditions throughout the day. Its eight articulated legs navigate furniture, rugs, and thresholds with surprising grace, carrying pots up to 8 inches wide and 15 lbs. The integrated light sensor tracks sun patterns and repositions your plant to catch morning rays, escape harsh afternoon glare, or retreat to shade—all automatically. Ideal for light-demanding plants like succulents, citrus, and herbs in apartments with limited window exposure. Advanced users can program custom patrol routes via the app, set "home base" locations, or integrate with smart blinds for coordinated light management. Battery lasts 5-7 days on a single charge with typical use. Fair warning: the spider-like locomotion takes some getting used to, but most owners report their Plant Stroller quickly becomes a beloved household character. Not recommended for homes with skittish pets or toddlers.	250	https://storage.googleapis.com/application-monitoring/plant-spider.jpg	https://storage.googleapis.com/application-monitoring/plant-spider-cropped.jpg
6	Plant Nodes	Listen more carefully to your plants.	Plant Nodes are compact wireless soil sensors that bring professional-grade monitoring to every pot in your collection. Each pack includes 5 weatherproof sensor sticks that measure soil moisture, pH levels, ambient temperature, and light intensity. Simply insert a node into any pot—indoors or out—and view real-time data from all your plants in a single dashboard. At just 4 inches tall, they're discreet enough for small succulents yet accurate enough for serious collectors managing rare aroids or orchids. The mesh network design means nodes relay data through each other, extending range throughout your home or garden without a separate hub. Battery life exceeds 12 months. Perfect entry point for beginners learning to read their plants, or as an expansion kit for existing Empower Plant setups. Compatible with all major smart home platforms and IFTTT for custom automations like triggering smart plugs for grow lights or sending watering reminders.	25	https://storage.googleapis.com/application-monitoring/nodes.png	https://storage.googleapis.com/application-monitoring/nodes-cropped.jpg
8	Plant Mood5	The mood ring for plants.	This is an example of what you can do with just a few things, a little imagination and a happy dream in your heart. I'm a water fanatic. I love water. There's not a thing in the world wrong with washing your brush. Everybody needs a friend. Here we're limited by the time we have.	155	https://storage.googleapis.com/application-monitoring/mood-planter.jpg	https://storage.googleapis.com/application-monitoring/mood-planter-cropped.jpg
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (id, productid, rating, customerid, description, created) FROM stdin;
1	3	5	\N	I've killed every plant I've ever owned until this thing. The color system is dead simple - I just glance at it when I walk by. My pothos has been thriving for 8 months now. Pro tip: the amber warning gives you about 2 days before your plant actually gets stressed, so don't panic water immediately.	2021-06-04 00:04:01.739234
2	3	4	\N	Solid product, works as advertised. Only minor gripe is the LED can be a bit bright at night if it's in your bedroom - had to put a small piece of tape over it. Would love a night mode in a future firmware update. The ceramic quality is excellent though, feels premium.	2021-06-04 00:04:26.233562
3	3	3	\N	It's fine for basic moisture monitoring but I found the light sensor pretty unreliable near windows with blinds - kept fluctuating. Also the pot drainage situation is awkward, you need the included saucer but it's not mentioned clearly. Works okay for my snake plant I guess.	2021-06-04 00:05:05.060103
4	4	4	\N	My kids are OBSESSED with this thing. We named our monstera "Gerald" and now he tells us when he's thirsty in a British accent. The novelty hasn't worn off after 3 months. Took about 10 days to calibrate, not the full 3 weeks. Only dock a star because the dome collects dust and is annoying to clean.	2021-06-04 00:12:33.553939
5	4	3	\N	Interesting concept but honestly feels more like a toy than a serious plant care tool. The "translations" are pretty generic - it basically just says variations of "water me" or "I'm happy" based on soil moisture. Was hoping for something more sophisticated. That said, my girlfriend loves it so it's staying.	2021-06-04 00:12:45.558259
6	4	2	\N	Returned after 2 weeks. The voice kept going off randomly at 3am saying "I sense change in my environment" every time our AC kicked on. Couldn't figure out how to adjust sensitivity and support was slow to respond. Cool idea, poor execution. Maybe wait for version 2.	2021-06-04 00:12:50.510322
7	5	3	\N	It works, but it's louder than expected - kind of a soft whirring/clicking when it walks. My lemon tree has never been healthier though, it follows the sun across my apartment perfectly. Just don't expect stealth. Also discovered it can't handle thick shag rugs, had to rearrange my living room.	2021-06-04 00:12:55.863029
8	5	2	\N	My cat destroyed this thing within a week. She was terrified at first, then decided it was prey. Ended up with a chewed leg and scratched dome. Maybe mention "not pet compatible" more prominently? The legs are NOT replaceable, so now I have a $250 paperweight.	2021-06-04 00:13:02.064086
9	5	1	\N	Complete disaster. It walked my fiddle leaf fig off a 2-inch step into my sunken living room. Pot shattered, soil everywhere, plant damaged. There's supposed to be edge detection but it clearly doesn't work on small drops. Customer service offered 20% off my next purchase. Seriously? Avoid.	2021-06-04 00:13:07.086163
10	6	5	\N	Best value in the Empower lineup. I have 23 houseplants and these nodes changed everything. The mesh network is legit - I have nodes in my garage and they relay through the kitchen ones no problem. Set up IFTTT to text me when any plant drops below threshold. Battery life is actually longer than advertised.	2021-06-04 00:13:13.186648
11	6	5	\N	Finally a product for serious collectors. I grow high-value anthuriums and the pH monitoring alone is worth the price. Caught a soil acidity problem before my crystallinum showed any visible stress. The data export feature is great for tracking seasonal patterns too.	2021-06-04 00:13:22.244425
12	6	4	\N	Solid sensors, no complaints on accuracy. Knocked off one star because the app UI is clunky - hard to rename nodes and the dashboard gets confusing with more than 8-10 plants. Also wish they came in colors, the white sticks look a bit clinical in terracotta pots. But functionally perfect.	2021-06-04 00:13:26.898053
13	4	3	\N	Gave this as a gift and the recipient thought it was hilarious for about a month. Now it mostly sits muted. Fun party trick but not essential. The HomeKit integration does work well though - it triggers our humidifier automatically when the plant asks for humidity.	2021-07-01 00:12:43.312186
14	4	3	\N	Had high hopes but the voice options are limited - only 5 personalities and they all sound slightly robotic. Would love to upload custom voices. Plant care aspect works fine, just expected more from the "AI" part at this price point.	2021-07-01 00:12:54.719873
15	4	3	\N	It's cute but the calibration period is real. For the first week it kept saying my plant was dying when it was perfectly fine. Apparently you need to water AND let it dry out at least twice during calibration for it to learn the range. Wish the manual explained that better.	2021-07-01 00:12:57.760686
16	4	3	\N	Middle of the road experience. The dome looks gorgeous on my shelf and guests always comment on it. Actual utility is debatable - I find myself checking soil moisture the old fashioned way anyway. More of a conversation piece than a care tool.	2021-07-01 00:13:00.140407
17	4	3	\N	Works okay with my calathea but completely useless with my cactus. It keeps saying the cactus is "critically dehydrated" when it's supposed to be dry. There should be plant type profiles to adjust sensitivity. Contacted support and they said it's "on the roadmap."	2021-07-01 00:13:00.97173
18	4	3	\N	The Alexa integration is actually the best part - I can ask "how is the monstera doing" and it gives a status report. Standalone voice announcements got annoying so I muted those. If you have a smart home setup, it's worth considering. Otherwise skip.	2021-07-01 00:13:01.665798
19	4	3	\N	Bought two, one worked great, one had constant connectivity issues and would lose calibration data. Exchanged the defective one and the replacement has been fine. Quality control might be an issue. The product concept is solid when it works.	2021-07-01 00:13:02.278934
20	5	2	\N	Cool concept, frustrating reality. The pathfinding gets confused by glass furniture - it sees reflections as obstacles. My coffee table creates an invisible force field apparently. Had to restrict it to one room which defeats the purpose of a mobile plant.	2021-07-01 00:14:33.534032
21	5	2	\N	Battery life is nowhere near 5-7 days if you have it actively tracking sunlight. More like 2-3 days in my south-facing apartment. And the charging dock is weirdly placed - the plant tilts at an awkward angle while charging. Design oversight.	2021-07-01 00:14:50.202678
22	5	2	\N	It scratched my hardwood floors. The rubber feet wore down after a few weeks and now the legs leave little marks. Empower sent replacement feet but they should have been more durable from the start. Otherwise the light-tracking actually works well.	2021-07-01 00:14:51.351695
23	5	2	\N	Scared the absolute life out of my elderly mother when she visited. She didn't know I had it and screamed when a plant walked past her in the hallway. Maybe I should have warned her but still - this thing is unsettling if you're not expecting it. Functional but creepy.	2021-07-01 00:14:54.516776
24	6	5	\N	These paid for themselves when they alerted me to overwatering my fiddle leaf during vacation. My plant sitter was killing it with kindness. The historical charts showed soil staying saturated for days. Saved a $200 plant with a $25 sensor. No brainer purchase.	2021-07-01 00:15:29.332914
25	6	5	\N	I maintain a small greenhouse and these are game changers. The outdoor rating is legit - survived a full New England winter. The mesh network reaches all corners of my setup, about 40 feet from the hub. Professional quality at consumer prices. Already ordered a second pack.	2021-07-01 00:15:30.670786
26	8	5	\N	Upgraded from the original Plant Mood and this version fixed all my complaints. The new LED diffuser is softer, no more blinding brightness. Also the Bluetooth range is noticeably better - works from two rooms away now. Worth upgrading if you liked the original.	2022-10-04 10:15:30.207862
27	8	5	\N	Perfect housewarming gift. I've given three of these now and everyone loves them. The setup is genuinely fool-proof - pair with app, pick your plant type, done. My technophobe aunt figured it out in 5 minutes. And the ceramic colors match any decor.	2022-10-04 10:15:34.928899
28	8	4	\N	Really nice product but I wish the pot sizes had more variety. 6 inches works for most houseplants but I'd love a larger version for my bird of paradise. The company says they're working on bigger sizes - hoping that comes soon. Otherwise flawless.	2022-10-04 10:15:39.249074
\.



--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_id_seq', 181, true);


--
-- Name: promo_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.promo_codes_id_seq', 1, true);

--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 8, true);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reviews_id_seq', 28, true);



--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: promo_codes promo_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promo_codes
    ADD CONSTRAINT promo_codes_pkey PRIMARY KEY (id);

--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: products products_title_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_title_key UNIQUE (title);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: cloudsqlsuperuser
--

-- REVOKE ALL ON SCHEMA public FROM cloudsqladmin;
-- REVOKE ALL ON SCHEMA public FROM PUBLIC;
-- GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;
-- GRANT ALL ON SCHEMA public TO PUBLIC;

--
-- Data for Name: promo_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.promo_codes (id, code, percent_discount, max_dollar_savings, is_active, expires_at, created_at) VALUES (3, 'SAVE20', 20, 50, true, '2025-09-09 00:05:48.263006', '2025-09-07 00:00:00');


--
-- PostgreSQL database dump complete
--

