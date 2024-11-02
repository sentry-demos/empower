<template>
  <div class="subscribe">
    <div class="text-content">
      <div className="checkout-error">
        <h1>We're having some trouble</h1>
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
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .checkout-error {
      width: 50rem;
  }
  .text-content {
    text-align: center;
    justify-content: center;
    margin-top: 10rem
  }
}
</style>