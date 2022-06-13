<template>
  <div class="subscribe">
    <div id="app">
      <div className="checkout-error">
        <h2>We're having some trouble</h2>
        <p>
          We were unable to process your order but will do everything we can to
          make it right. Please reach out to us if you have
          been charged or have any questions.
        </p>
      </div>
    </div>
  </div>
</template>

<style>
@media (min-width: 1px) {
  .subscribe {
    min-height: 50vh;
    display: flex;
    align-items: center;
  }
  .checkout-error {
      width: 50rem;
  }
}
</style>