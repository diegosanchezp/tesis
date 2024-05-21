export interface SwapEvent extends CustomEvent {
    detail: {
        target_element_id: string
        position: "innerHTML" | "outerHTML" | InsertPosition
        text_html: string
    }
}

/**
 * Imitates the htmx hx-swap attribute
 * https://htmx.org/attributes/hx-swap/
 */
export function hxSwap(evt: SwapEvent){
    // Search for the target element
    const targetElement = document.getElementById(evt.detail.target_element_id)

    // If the target element is not found, log an error and exit
    if(!targetElement){
        console.error(`Element with id ${evt.detail.target_element_id} not found`)
        return
    }
    const { position, text_html } = evt.detail

    // Replace the content of the target element
    if(position === "innerHTML"){
        targetElement.innerHTML = text_html
    } else if(position === "outerHTML"){
        targetElement.outerHTML = text_html
    } else {
        targetElement.insertAdjacentHTML(position, text_html)
    }
}

/**
 * Adds the event listeners that are required for htmx utils to work 
 */
export function initHTMXutils(){
    document.body.addEventListener("jsSwap", hxSwap)
}
