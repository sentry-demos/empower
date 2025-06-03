<template>
    <div class="container">
      
      <main class="hero-bg-img">
        <div class="text-content">
            <h1>Empower your plants</h1>
            <p>Keep your houseplants happy.</p>
            <button class="browse-button">Browse products</button>
        </div>
      </main>
      
    </div>
  </template>
  
  <script>
  export default {
    name: "HomePage",
  };
  </script>
  
  <style scoped>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    font-family: Arial, sans-serif;
  }

  .hero-bg-img {
    width: 100%;
    height: 100vh; /* Full viewport height */
    display: flex;
    align-items: center;
    color: white;
    background-image: url("@/assets/plants-background-img.jpg"); /* Replace with your image path */
    background-size: cover;
    background-position: center;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 10px 50px;
    background-color: #fff;
  }
  
  .logo {
    height: 40px;
  }
  
  .nav a {
    margin: 0 15px;
    text-decoration: none;
    color: black;
    font-weight: bold;
  }
  
  .main-content {
    display: flex;
    padding: 20px;
    background-image: url("@/assets/plants-background-img.jpg"); /* Replace with your image path */
    background-size: cover;
    background-position: center;
  }
  
  .text-content {
    margin-bottom: 20px;
    margin-left: 50px;
  }
  
  .text-content h1 {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
  }
  
  .text-content p {
    font-size: 1rem;
    margin: 5px 0;
    color: #666;
  }
  
  .browse-button {
    padding: 10px 20px;
    background-color: #2c3e50;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    border-radius: 5px;
    margin-top: 50px
  }
  
  .browse-button:hover {
    background-color: #34495e;
  }
  
  .image-content {
    width: 100%;
    max-width: 600px;
  }
  
  .plants-image {
    width: 100%;
    height: auto;
    border-radius: 10px;
  }
  
  .footer {
    padding: 20px;
  }
  h1{
    color: black;
  }
  
  .report-bug {
    background: none;
    border: none;
    color: #555;
    cursor: pointer;
    font-size: 0.9rem;
  }
  </style>