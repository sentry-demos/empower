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
-- Name: tools; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tools (
    id integer NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    sku character varying NOT NULL,
    image character varying NOT NULL,
    price integer NOT NULL
);


ALTER TABLE public.tools OWNER TO postgres;

--
-- Name: tools_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tools_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tools_id_seq OWNER TO postgres;

--
-- Name: tools_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tools_id_seq OWNED BY public.tools.id;


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
-- Name: tools id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tools ALTER COLUMN id SET DEFAULT nextval('public.tools_id_seq'::regclass);


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
3	Plant Mood	The mood ring for plants.	This is an example of what you can do with just a few things, a little imagination and a happy dream in your heart. I'm a water fanatic. I love water. There's not a thing in the world wrong with washing your brush. Everybody needs a friend. Here we're limited by the time we have.	155	https://storage.googleapis.com/application-monitoring/mood-planter.jpg	https://storage.googleapis.com/application-monitoring/mood-planter-cropped.jpg
4	Botana Voice	Lets plants speak for themselves.	Now we don't want him to get lonely, so we'll give him a little friend. Let your imagination just wonder around when you're doing these things. Let your imagination be your guide. Nature is so fantastic, enjoy it. Let it make you happy.	175	https://storage.googleapis.com/application-monitoring/plant-to-text.jpg	https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg
5	Plant Stroller	Because plant don't have feet.	Look at them little rascals. There are no limits in this world. That easy. Just make a decision and let it go. I was blessed with a very steady hand; and it comes in very handy when you're doing these little delicate things. Take your time. Speed will come later.	250	https://storage.googleapis.com/application-monitoring/plant-spider.jpg	https://storage.googleapis.com/application-monitoring/plant-spider-cropped.jpg
6	Plant Nodes	Listen more carefully to your plants.	By now you should be quite happy about what's happening here. Put your feelings into it, your heart, it's your world. Let's get wild today. This is the fun part	25	https://storage.googleapis.com/application-monitoring/nodes.png	https://storage.googleapis.com/application-monitoring/nodes-cropped.jpg
8	Plant Mood5	The mood ring for plants.	This is an example of what you can do with just a few things, a little imagination and a happy dream in your heart. I'm a water fanatic. I love water. There's not a thing in the world wrong with washing your brush. Everybody needs a friend. Here we're limited by the time we have.	155	https://storage.googleapis.com/application-monitoring/mood-planter.jpg	https://storage.googleapis.com/application-monitoring/mood-planter-cropped.jpg
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (id, productid, rating, customerid, description, created) FROM stdin;
1	3	5	\N	\N	2021-06-04 00:04:01.739234
2	3	4	\N	\N	2021-06-04 00:04:26.233562
3	3	3	\N	\N	2021-06-04 00:05:05.060103
4	4	4	\N	\N	2021-06-04 00:12:33.553939
5	4	3	\N	\N	2021-06-04 00:12:45.558259
6	4	2	\N	\N	2021-06-04 00:12:50.510322
7	5	3	\N	\N	2021-06-04 00:12:55.863029
8	5	2	\N	\N	2021-06-04 00:13:02.064086
9	5	1	\N	\N	2021-06-04 00:13:07.086163
10	6	5	\N	\N	2021-06-04 00:13:13.186648
11	6	5	\N	\N	2021-06-04 00:13:22.244425
12	6	4	\N	\N	2021-06-04 00:13:26.898053
13	4	3	\N	\N	2021-07-01 00:12:43.312186
14	4	3	\N	\N	2021-07-01 00:12:54.719873
15	4	3	\N	\N	2021-07-01 00:12:57.760686
16	4	3	\N	\N	2021-07-01 00:13:00.140407
17	4	3	\N	\N	2021-07-01 00:13:00.97173
18	4	3	\N	\N	2021-07-01 00:13:01.665798
19	4	3	\N	\N	2021-07-01 00:13:02.278934
20	5	2	\N	\N	2021-07-01 00:14:33.534032
21	5	2	\N	\N	2021-07-01 00:14:50.202678
22	5	2	\N	\N	2021-07-01 00:14:51.351695
23	5	2	\N	\N	2021-07-01 00:14:54.516776
24	6	5	\N	\N	2021-07-01 00:15:29.332914
25	6	5	\N	\N	2021-07-01 00:15:30.670786
26	8	5	\N	\N	2022-10-04 10:15:30.207862
27	8	5	\N	\N	2022-10-04 10:15:34.928899
28	8	4	\N	\N	2022-10-04 10:15:39.249074
\.


--
-- Data for Name: tools; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tools (id, name, type, sku, image, price) FROM stdin;
1	allen wrench	wrench	asyqtzmrhsabqxri	wrench.png	5672
2	allen wrench	wrench	vkvnmvpnkagfnrkr	wrench.png	912
3	alligator wrench	wrench	wlzfznigebfrharg	wrench.png	8722
4	annular ring nails	nails	zkvsixjthreumjut	nails.png	7870
5	annular ring nails	nails	irfpkztydpfeueye	nails.png	7325
6	annular ring nails	nails	kxljbwggsrtujclc	nails.png	887
7	armorers wrench	wrench	bpiplgewiwnbvqfi	wrench.png	5199
8	armorers wrench	wrench	rztpqcgnltqnjaso	wrench.png	5578
9	armorers wrench	wrench	ygwzoznsauarvomp	wrench.png	3791
10	ball peen hammer	hammer	lmgcqxgahidfnejm	hammer.png	159
11	ball peen hammer	hammer	arovnvkuwneujcox	hammer.png	3065
12	ball peen hammer	hammer	avouvokblpdttmqi	hammer.png	8213
13	basin wrench	wrench	heleijzdxthmnsct	wrench.png	5195
14	basin wrench	wrench	gkvrujhgoxduzswk	wrench.png	9694
15	bionic wrench	wrench	bhxrvasbcnlpijfs	wrench.png	7928
16	blacksmith hammer	hammer	wfffdlwcmanycxei	hammer.png	7594
17	blacksmith hammer	hammer	tcohxiksqgaknpnc	hammer.png	9121
18	blacksmith hammer	hammer	anuoqioixnkkowpa	hammer.png	8982
19	blocking hammer	hammer	wgttbllcaucbojhp	hammer.png	2395
20	box nails	nails	hykjhcncclptxfjb	nails.png	740
21	box nails	nails	adijabdsruvqkiwe	nails.png	5576
22	box-ended wrench	wrench	lbszeucgyyvwmjmk	wrench.png	8543
23	brass hammer	hammer	pcnifwlrllpujpzm	hammer.png	2522
24	brass hammer	hammer	evrfjnedushxmvmv	hammer.png	2364
25	brass hammer	hammer	vqjwiuqfctzaubri	hammer.png	3128
26	brick hammer	hammer	mkivcjodswzmoibi	hammer.png	4103
27	bung wrench	wrench	dxytwglmbajqabwb	wrench.png	8130
28	bung wrench	wrench	hptviwfmxbssluxp	wrench.png	6581
29	bushing hammer	hammer	updkbakkwoxnhbxj	hammer.png	6647
30	bushing hammer	hammer	bjyvfgjhqsyfborh	hammer.png	2287
31	bushing hammer	hammer	ptoedlygzuukqsjy	hammer.png	5300
32	casing nails	nails	ofinrxljbhhwqzap	nails.png	5535
33	casing nails	nails	twmayioxugxfmbgq	nails.png	2462
34	casing nails	nails	niumupgzjzsqrjno	nails.png	2337
35	chasing hammer	hammer	nxdzpjpddfxsoygr	hammer.png	1124
36	chasing hammer	hammer	upjbpgvxbbdmoqra	hammer.png	8704
37	chasing hammer	hammer	kkqefxnyxjbyefao	hammer.png	6687
38	claw hammer	hammer	bhuweevachzmskta	hammer.png	3324
39	club hammer	hammer	xlezvizjlpoocqvz	hammer.png	7256
40	club hammer	hammer	wfwhhejsklvvmbuh	hammer.png	1700
41	combination wrench	wrench	nkzqlafiafmnrbhw	wrench.png	4073
42	combination wrench	wrench	orgcisnxnlachmip	wrench.png	7721
43	combination wrench	wrench	wnushigyudgldtgl	wrench.png	6224
44	cone wrench	wrench	bkqtjpshztxcdlyw	wrench.png	4938
45	cone wrench	wrench	vivwllmitpkizrme	wrench.png	8651
46	cone wrench	wrench	vltmkrcmoegwgfza	wrench.png	7314
47	cross peen hammer	hammer	naaqsymjutzchdwy	hammer.png	7618
48	cross peen pin hammer	hammer	aqacrdrmlzyyzeul	hammer.png	7945
49	cross peen pin hammer	hammer	bqgokmpzgudiybvr	hammer.png	3933
50	crowfoot wrench	wrench	iofcpxziuolhalah	wrench.png	4556
51	crowfoot wrench	wrench	ikeylnnvehleqsxh	wrench.png	9885
52	cut flooring nails	nails	wqkulatumgfvldzd	nails.png	8119
53	cut flooring nails	nails	hoklakwjhdxshugx	nails.png	5647
54	dead blow hammer	hammer	cffbrksscedvzipt	hammer.png	5528
55	dead blow hammer	hammer	viyspuowupgixacu	hammer.png	3142
56	dead blow hammer	hammer	pgejnzgainbfhuos	hammer.png	4381
57	die stock holder wrench	wrench	jhsaecvetnktffph	wrench.png	6027
58	die stock holder wrench	wrench	altjtdtmcwniygak	wrench.png	3423
59	dog bone wrench	wrench	fccuewmzalukltkc	wrench.png	8879
60	dog bone wrench	wrench	nbaambutehmyyvxp	wrench.png	2669
61	dog bone wrench	wrench	evpbxygdmsfrxogx	wrench.png	2405
62	drywall hammer	hammer	asqudkthmzpxmisl	hammer.png	1078
63	drywall hammer	hammer	dibbkltouvpbxobx	hammer.png	6612
64	duplex nails	nails	ikprbhoomzemlmvo	nails.png	3911
65	electricians hammer	hammer	tcfcfwxmffxbhsnw	hammer.png	1286
66	engineering hammer	hammer	ygfglxbzwiptoncj	hammer.png	4737
67	engineering hammer	hammer	oudnojdknalaanbl	hammer.png	2076
68	fan clutch wrench	wrench	tkgnvmegwildfioi	wrench.png	1655
69	fan clutch wrench	wrench	dtzhkwcivxscojnq	wrench.png	4731
70	fan clutch wrench	wrench	vvaampnllwyiqwqi	wrench.png	9968
71	finishing nails	nails	rfkjkawgyjgsrnjx	nails.png	806
72	finishing nails	nails	kcgwezietnhikgfw	nails.png	4701
73	finishing nails	nails	ldlgqrmiinizbjua	nails.png	6800
74	fire hydrant wrench	wrench	xgmqgfmdltecxsyb	wrench.png	3145
75	fire hydrant wrench	wrench	jclaejidrumhuwbt	wrench.png	9776
76	flare nut wrench	wrench	vaziboxpxcgrevwq	wrench.png	9738
77	flare nut wrench	wrench	mqxgitbsalmoytas	wrench.png	3960
78	flare nut wrench	wrench	oxztelegnjagrnvi	wrench.png	302
79	framing hammer	hammer	nvuhbztuupkjufgt	hammer.png	4181
80	framing hammer	hammer	enlsxgqzrzmscuyf	hammer.png	7571
81	garbage disposal wrench	wrench	wkcpqmdrcjkbxzyx	wrench.png	3731
82	garbage disposal wrench	wrench	mykqhgwkhuscewyk	wrench.png	5907
83	garbage disposal wrench	wrench	ausjvjvowubeghox	wrench.png	5041
84	hammer wrench	wrench	icczobbfeqrmepzr	wrench.png	2086
85	hatchet hammer	hammer	eocbgszpyysliugj	hammer.png	4040
86	impact wrench	wrench	ngyyutmxemirdjbx	wrench.png	625
87	impact wrench	wrench	hixkrvqgelfjacnt	wrench.png	3039
88	impact wrench	wrench	ajnwfbfxnoozrxty	wrench.png	5469
89	joiners mallet	hammer	oxrszsjkmuysuppa	hammer.png	2524
90	joiners mallet	hammer	zaszxmbtqydjydxu	hammer.png	311
91	joiners mallet	hammer	vrxkxyxabastciom	hammer.png	6812
92	linemans hammer	hammer	svxeelfkkrabpojf	hammer.png	213
93	linemans hammer	hammer	xliyqapactzrdsxx	hammer.png	3151
94	linemans hammer	hammer	hpekcnzzyaitcnvi	hammer.png	7639
95	lug wrench	wrench	vvotghxhoygeebuz	wrench.png	8803
96	lug wrench	wrench	vwurhpwlfofwlpoz	wrench.png	8644
97	masonry nails	nails	ckmzjaqjqxwpbhxn	nails.png	9836
98	mechanics hammer	hammer	ipglzkvxmfzatioy	hammer.png	1413
99	monkey wrench	wrench	lzfqqskibppeeoah	wrench.png	856
100	monkey wrench	wrench	hwapecrmnxzvkqcv	wrench.png	7571
101	monkey wrench	wrench	jdpdyjiujchwtnla	wrench.png	4131
102	oil filter wrench	wrench	zqmtlwhzqcyuters	wrench.png	1040
103	oil filter wrench	wrench	mpqbpztslfqazwzq	wrench.png	4634
104	oil filter wrench	wrench	mhitgjkpcbufthto	wrench.png	4392
105	open-ended wrench	wrench	bbjyqsqnjjjpmrth	wrench.png	8329
106	open-ended wrench	wrench	vspotybxlyfhsawk	wrench.png	4583
107	pedal wrench	wrench	txybgtchurpxpume	wrench.png	666
108	pedal wrench	wrench	oimmgyurvkqxpzbq	wrench.png	137
109	pipe wrench	wrench	yuagytoirhhugnil	wrench.png	6368
110	pipe wrench	wrench	rgcfgxkgraexckrj	wrench.png	8736
111	piton hammer	hammer	wpeewsoshpqyoxiv	hammer.png	8083
112	piton hammer	hammer	ygewnpiwxjzkbatt	hammer.png	1630
113	piton hammer	hammer	rislatttoxyzbetf	hammer.png	5543
114	planishing hammer	hammer	fikficjsqwwxfhlc	hammer.png	7499
115	pliers wrench	wrench	lyqqeuvoajssiwhu	wrench.png	4163
116	pliers wrench	wrench	aerilnezsuuurngt	wrench.png	1274
117	pliers wrench	wrench	hirfrnckgccdtwit	wrench.png	8668
118	plumbers wrench	wrench	wsjpbwgdgoppeydi	wrench.png	294
119	plumbers wrench	wrench	krrgriznjvtvjxhu	wrench.png	9314
120	plumbers wrench	wrench	wpxaulnrbgoeqocu	wrench.png	4078
121	power hammer	hammer	llnezgddutmzirnf	hammer.png	4693
122	ratcheting wrench	wrench	ecpsgkwzqoyedvsp	wrench.png	5050
123	rip hammer	hammer	dokigqhbnmiguuzv	hammer.png	9324
124	rip hammer	hammer	zqajvhitwyoiwvdc	hammer.png	2676
125	rock hammer	hammer	zhldeuptkajgfqcg	hammer.png	106
126	rock hammer	hammer	qkvzdmpyxyvdgekj	hammer.png	3970
127	rock hammer	hammer	lknudoznxsjnfgii	hammer.png	1173
128	roofing nails	nails	rwmlvabsbijfgeje	nails.png	7273
129	rubber mallet	hammer	tiejgjbfjtpfrcae	hammer.png	3208
130	rubber mallet	hammer	nfeddiapskpfpulp	hammer.png	5065
131	scaling hammer	hammer	bpwbjcsdmcwtvfps	hammer.png	9350
132	scaling hammer	hammer	tjgdglrsmyhqjkaj	hammer.png	2564
133	scaling hammer	hammer	bpioalyocbjwkjpw	hammer.png	7381
134	scutch hammer	hammer	mhohwrxfsymgafah	hammer.png	8851
135	scutch hammer	hammer	dnnyrxbbxxbtbjyh	hammer.png	5813
136	scutch hammer	hammer	lhsykvjpbsowadkp	hammer.png	8111
137	shingle hammer	hammer	cayublfwsrslbgdc	hammer.png	1909
138	sledge hammer	hammer	mnxjkirhuwdvzrik	hammer.png	2072
139	sledge hammer	hammer	mtdzicwwbhbzonxh	hammer.png	4076
140	sledge hammer	hammer	vgsheqkgodfzkzwc	hammer.png	6477
141	socket wrench	wrench	ljcdubzmgncfwwct	wrench.png	8847
142	soft-faced hammer	hammer	sziekiofvtznpzac	hammer.png	5790
143	spanner wrench	wrench	fdxgokktxzrsfluh	wrench.png	4093
144	spark plug wrench	wrench	mzgjhwuihwiyyoiv	wrench.png	8897
145	spike maul hammer	hammer	bgqwvujifropxqgo	hammer.png	9035
146	spike maul hammer	hammer	bkhqxxnolpofwosy	hammer.png	100
147	spiral flooring nails	nails	xerwinsxqmdrfytz	nails.png	1371
148	spiral flooring nails	nails	quvujczugejkmhod	nails.png	4717
149	spiral flooring nails	nails	dsgylsdieqlcdyby	nails.png	2654
150	spoke wrench	wrench	wuyfwihjppxxprow	wrench.png	9275
151	spoke wrench	wrench	thwfstmlplnlmqoj	wrench.png	3539
152	spud wrench	wrench	edlqwctepadptpsx	wrench.png	3533
153	spud wrench	wrench	aorgefncbuygazyz	wrench.png	3433
154	spud wrench	wrench	kexcivjjjuqyimdy	wrench.png	6065
155	stone sledge hammer	hammer	swtwlvcfsryxyejp	hammer.png	7055
156	stone sledge hammer	hammer	detajddowpkrmtlz	hammer.png	8003
157	stone sledge hammer	hammer	kiabjtzmrjjtlkvz	hammer.png	6755
158	straight peen hammer	hammer	omjtxmtgjnouwwvz	hammer.png	486
159	straight peen hammer	hammer	rszrlmsrdgersmak	hammer.png	7500
160	straight peen hammer	hammer	eubzaepvkjxkzymz	hammer.png	7640
161	strap wrench	wrench	ssyiapinbmuziavy	wrench.png	5060
162	stubby wrench	wrench	qsiwanfrrmzudhyv	wrench.png	7742
163	stubby wrench	wrench	rylkcbrdruhwcyeq	wrench.png	8971
164	stubby wrench	wrench	sqzpwjlwpsvdkmvv	wrench.png	9599
165	tack hammer	hammer	iswuklbgvlmuwqbj	hammer.png	9353
166	tack hammer	hammer	sonqscmuajbvcpnn	hammer.png	3804
167	tack hammer	hammer	hjwttvpqaxvfsekd	hammer.png	8795
168	tap wrench	wrench	xkjlxhicexqahwxt	wrench.png	2660
169	tension wrench	wrench	sgcgjgxkewzyevdj	wrench.png	529
170	tinners hammer	hammer	phdojdgehheteqky	hammer.png	1563
171	toolmakers hammer	hammer	ukxvolljzswhwipb	hammer.png	3208
172	toolmakers hammer	hammer	gdczuxloowbkkhkt	hammer.png	997
173	toolmakers hammer	hammer	ttsmbmdxcvyplafq	hammer.png	8408
174	torque wrench	wrench	jfagdimhysntpstl	wrench.png	3137
175	torque wrench	wrench	tdmygwiirjxiktvh	wrench.png	8682
176	torque wrench	wrench	wjpljttrudcagxev	wrench.png	8940
177	trim hammer	hammer	ymclroesmoixlnzd	hammer.png	3756
178	trim hammer	hammer	gcubpzcmxkgewwqy	hammer.png	4342
179	trim hammer	hammer	cjqjcvfssbealiei	hammer.png	2972
180	welding hammer	hammer	avsllxdyeltrvwim	hammer.png	7203
181	welding hammer	hammer	vlqbxjpzrfxmfqhw	hammer.png	6148
\.


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_id_seq', 181, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 8, true);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reviews_id_seq', 28, true);


--
-- Name: tools_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tools_id_seq', 181, true);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


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
-- Name: tools tools_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tools
    ADD CONSTRAINT tools_pkey PRIMARY KEY (id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: cloudsqlsuperuser
--

-- REVOKE ALL ON SCHEMA public FROM cloudsqladmin;
-- REVOKE ALL ON SCHEMA public FROM PUBLIC;
-- GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;
-- GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

