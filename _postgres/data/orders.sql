--
-- Orders, for the agent's order tools. Kept out of empowerplant.sql so that
-- file stays a pg_dump.
--
-- deploy_project.sh runs every .sql file here in sorted order, so this runs
-- after empowerplant.sql.
--

SET search_path = public;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--
-- Read by GET /orders and GET /orders/<id>, and written by
-- POST /orders/<id>/cancel in flask.
-- Order 445 is the one the demo cancels. Its cancellation never completes (the
-- payment provider times out), so flask puts it back to processing and it stays
-- cancellable: the demo can be run against it again without a reseed.
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    email character varying NOT NULL,
    status character varying(32) NOT NULL,
    total integer NOT NULL,
    items character varying NOT NULL,
    shipping_address character varying NOT NULL,
    payment_intent character varying NOT NULL,
    created timestamp without time zone DEFAULT now()
);

ALTER TABLE public.orders OWNER TO postgres;

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);

INSERT INTO public.orders (id, email, status, total, items, shipping_address, payment_intent, created) VALUES
(443, 'plant.lover@example.com', 'delivered', 155, '1 x Botana Voice', '123 Main Street, San Francisco, CA 94122', 'pi_3PmockEmpower443', '2026-09-02 10:14:00'),
(444, 'plant.lover@example.com', 'shipped', 330, '1 x Plant Mood, 1 x Plant Nodes', '123 Main Street, San Francisco, CA 94122', 'pi_3PmockEmpower444', '2026-10-12 16:41:00'),
(445, 'plant.lover@example.com', 'processing', 485, '1 x Plant Mood, 1 x Plant Stroller, 1 x Plant Nodes', '123 Main Street, San Francisco, CA 94122', 'pi_3PmockEmpower445', '2026-10-19 09:03:00'),
(446, 'plant.lover@example.com', 'processing', 25, '1 x Plant Mood5', '123 Main Street, San Francisco, CA 94122', 'pi_3PmockEmpower446', '2026-10-20 18:27:00');
