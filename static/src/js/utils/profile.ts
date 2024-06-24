import { openModal, closeModalRPC, openModalRPC } from 'js/utils/modal'
import htmx from 'htmx.org';
import { initHTMXutils } from 'js/utils/htmx'

export function setupProfile(){
    window.getCareerInfo = async (getModalUrl: string) => {
        const modalTargetId = "#career-selector-modal"
        await htmx.ajax(
            "GET", getModalUrl, {
            swap: "innerHTML",
            target: modalTargetId
        })
        openModal({modalTargetId})
    }

    document.body.addEventListener("closeModal", closeModalRPC)
    document.body.addEventListener("openModal", openModalRPC)

    initHTMXutils()
}



