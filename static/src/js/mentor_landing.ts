import htmx from 'htmx.org';
import { initHTMXutils } from 'js/utils/htmx'

/**
 * Converts a FormData object to a query string
 */
function formDataToQueryParam(formData: FormData): string {
    const params = new URLSearchParams();
    for (const pair of formData.entries()) {
        params.append(pair[0], pair[1]);
    }
    return params.toString();
}

const paginationContainerId = "pagination_container"

/**
 * Re-attaches the pagination event listener after the table is re-rendered
 */
function reAttachPagination(){
    const paginationContainer = document.getElementById(paginationContainerId)
    if(!paginationContainer) { console.error("Pagination container not found"); return }
    console.log("Re-attaching pagination")
    paginationContainer.addEventListener("click", processPagination)
}

/**
* Re-renders the mentorship request table when the pagination links are clicked
*/
function processPagination(evt: MouseEvent){
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

// Listen for the reAttachPagination event that server sends when the table is re-rendered
document.addEventListener("reAttachPagination", reAttachPagination)

document.addEventListener("DOMContentLoaded", () => {
    reAttachPagination()
})

document.addEventListener("htmx:afterSwap",()=>{
    console.log("htmx:afterSwap")
})
initHTMXutils()
