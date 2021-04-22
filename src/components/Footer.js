import './footer.css';

function Footer() {
  return (
    <footer id="footer">
      <div>
        <h2 className="h3">Sign up for plant tech news</h2>
        <form>
          <label htmlFor="email-subscribe">Email</label>
          <input
            type="email"
            name="email-subscribe"
            id="email-subscribe"
          ></input>
          <input type="submit" value="Subscribe"></input>
        </form>
        <p>© 2021 • Empower Plant</p>
      </div>
    </footer>
  );
}

export default Footer;
