import { Modal } from 'flowbite'

document.addEventListener("DOMContentLoaded", ()=>{
  // select the two elements that we'll work with
  const $buttonElement = document.querySelector('#button') as HTMLButtonElement;
  const $modalElement = document.querySelector('#modal') as HTMLElement;

  // create a new modal component
  const modal = new Modal($modalElement, {closable: true});

  // toggle the visibility of the modal when clicking on the button
  $buttonElement.addEventListener('click', () => modal.toggle());
})
