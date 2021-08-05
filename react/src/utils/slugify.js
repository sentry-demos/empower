const slugify = (str) => {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]/gi, ' ')
    .trim()
    .replace(/\s+/, ' ');
};

export default slugify;