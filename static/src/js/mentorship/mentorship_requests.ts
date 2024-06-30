import htmx from 'htmx.org';
import { formDataToQueryParam } from 'js/utils'
import { Modal } from 'flowbite';
import type { ModalOptions } from 'flowbite';

const paginationContainerId = "pagination_container"

const boolMap = {
    "true": true,
    "false": false,
    "True": true,
    "False": false,
}

type BoolMapKeys = keyof typeof boolMap;
/**
* Fetches the student info and displays it in a modal
* @param studentUrl - The URL to fetch the student info from
*/
export async function getStudentInfo(studentUrl:string, withMentorshipName: BoolMapKeys) {
    const modalTarget = "#student-info-modal"

    console.log(boolMap[withMentorshipName])
    await htmx.ajax("GET", studentUrl, {
        target: `${modalTarget}`,
        swap: "innerHTML",
        values: {
            with_mentorship_name: Boolean(boolMap[withMentorshipName])
        }
    })

    const modalElement = document.querySelector(modalTarget) as HTMLElement

    const modalOptions: ModalOptions = {
        closable: true,
        placement: 'bottom-right',
    }
    const modal = new Modal(modalElement,modalOptions);

    // Show the modal after we get its HTML
    modal.show()

    const closeBtn = modalElement.querySelector("#close-btn")

    // Close the modal when X button is clicked
    closeBtn.addEventListener("click", ()=>{
        modal.hide()
    })

}

/**
 * Re-attaches the pagination event listener after the table is re-rendered
 */
export function reAttachPagination(){
    const paginationContainer = document.getElementById(paginationContainerId)
    if(!paginationContainer) { console.error("Pagination container not found"); return }
    paginationContainer.addEventListener("click", processPagination)
}

/**
* Re-renders the mentorship request table when the pagination links are clicked
* @param evt - The click event
*/
export function processPagination(evt: MouseEvent){
    evt.preventDefault()

    // Get the page Query Param from templates/components/pagination.html
    const anchor = evt.target as HTMLAnchorElement
    const pageURL: string | null = anchor.getAttribute("href") 
    if(!pageURL) return

    // Get the table filters
    const table_filters = document.getElementById("table_filters")
    if(!table_filters) { console.error("Table #mentorship_req_table not found"); return }
    const formData = new FormData(table_filters as HTMLFormElement)
    const filterQueryParams = formDataToQueryParam(formData);
    const reqURL = `${pageURL}${filterQueryParams}`

    // Re-render the table
    htmx.ajax("GET",reqURL, {
        target: `#table_form`,
        swap: "outerHTML"
    }).then(() => {
        reAttachPagination()
    })
}

/**
 * Initializes the mentorship requests table pagination event listeners
 * see templates/mentor/mentorship_req_table.html
 */
export function initMentoshipPagination(){
    // Listen for the reAttachPagination event that server sends when the table is re-rendered
    document.addEventListener("reAttachPagination", reAttachPagination)

    document.addEventListener("DOMContentLoaded", () => {
        reAttachPagination()
    })

    // For seeing the details of a student in the 
    // mentorship request table
    window.getStudentInfo = getStudentInfo
}
