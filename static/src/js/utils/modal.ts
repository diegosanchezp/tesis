import { Modal } from 'flowbite';
import type { ModalOptions } from 'flowbite';

interface ModalParams {
    modalTargetId: string
}

interface GetModalOptions extends ModalParams {
    options?: ModalOptions
}

export function getModal(params: GetModalOptions){
    const { modalTargetId, options } = params

    const modalElement = document.querySelector(modalTargetId) as HTMLElement

    const modalOptions: ModalOptions = {
        closable: true,
        placement: 'bottom-right',
        ...options
    }
    const modal = new Modal(modalElement,modalOptions);

    const closeBtn = modalElement.querySelector("#close-btn") as HTMLButtonElement

    // Close the modal when X button is clicked
    closeBtn.addEventListener("click", ()=>{
        modal.hide()
    })

    return { modal, closeBtn }
}


/**
 * Opens a modal with the given content
 */
export function openModal(params: GetModalOptions){
    const { modalTargetId, options } = params

    const { modal } = getModal({modalTargetId, options})

    // Show the modal after we get its HTML
    modal.show()
}

export function closeModal(params: ModalParams){
    const { modalTargetId } = params

    const { closeBtn } = getModal({modalTargetId})

    // Hide the modal triggering click event
    // Because the backdrop is duplicated when the modal is constructed again
    closeBtn.click()
}

export interface ModalEvtDetail {
    modalTargetId: ModalParams['modalTargetId']
}
export interface ModalEvent extends CustomEvent {
    detail: ModalEvtDetail
}

/** RPC method to close a modal */
export function closeModalRPC(evt: ModalEvent){
    const { modalTargetId } = evt.detail
    closeModal({modalTargetId})
}


export function openModalRPC(evt: ModalEvent){
    const { modalTargetId } = evt.detail
    openModal({modalTargetId})
}
