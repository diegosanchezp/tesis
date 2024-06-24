import { initFlowbite } from 'flowbite';
import htmx from 'htmx.org'

export interface SwapEvtDetail {
    target_element_id: string
    position: "innerHTML" | "outerHTML" | InsertPosition
    text_html: string
}
export interface SwapEvent extends CustomEvent {
    detail: {
        swaps: SwapEvtDetail[]
    }
}

/**
 * Imitates the htmx hx-swap attribute
 * https://htmx.org/attributes/hx-swap/
 */
export function hxSwap(evt: SwapEvent){
    // Search for the target element
    for( const swap of evt.detail.swaps){
        let targetElement = document.getElementById(swap.target_element_id)

        // If the target element is not found, log an error and exit
        if(!targetElement){
            console.error(`Element with id ${swap.target_element_id} not found`)
            return
        }
        const { position, text_html } = swap

        // Replace the content of the target element
        if(position === "innerHTML"){
            targetElement.innerHTML = text_html
        } else if(position === "outerHTML"){
            targetElement.outerHTML = text_html
        } else {
            targetElement.insertAdjacentHTML(position, text_html)
        }

        // Enable htmx behaviour for replaced element
        // https://htmx.org/api/#process

        // Get the target element again
        targetElement = document.getElementById(swap.target_element_id)

        // If the target element is not found, log an error and exit
        if(!targetElement){
            console.error(`Element with id ${swap.target_element_id} not found`)
            return
        }
        htmx.process(targetElement)
    }
}

/** Renders django messages as flowbite toasts */
export function renderMessagesAsToasts(evt: SwapEvent){

    // Create a div element that serves as a placeholder for the toasts
    // This will be useful for the hxSwap call above
    const div = document.createElement('div')
    div.setAttribute("id", "toast_area")

    // Insert it into the body as the first child element
    document.body.insertBefore(div, document.body.firstChild)

    // Replace the div with the django messages html
    hxSwap(evt)

    // Init flowbite so new toasts can be dismissed
    initFlowbite()
}

/**
 * Adds custom event listeners that are required for htmx utils to be called from the server (RPC)
 */
export function initHTMXutils(){
    document.body.addEventListener("jsSwap", hxSwap)
    document.body.addEventListener("renderMessagesAsToasts", renderMessagesAsToasts)
}

