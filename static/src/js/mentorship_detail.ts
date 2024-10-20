import 'flowbite';
import { initModals } from 'flowbite';
import { initHTMXutils } from 'js/utils/htmx'
import { initTablePagination } from './utils/table'
import { initMentorReqTable } from './mentor/shared'


// Add the event listeners for the pagination in the mentorship requests table
initTablePagination("mentorship_req_table")

// Init events listeners for RPC communication beteween the server and the browser
initHTMXutils()

initMentorReqTable()

document.addEventListener("DOMContentLoaded", ()=>{

    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Re-attach flowbite event listeners for 'Eliminar' btn only if we
        // are showing the reading state of a mentorship 
        const editElement = event.detail.elt.querySelector('#mentorship-form')
        const isFromEdit = Boolean(editElement)
        if(event.detail.elt.id === 'mentorship-info' && !isFromEdit){
            initModals()
        }
    });
})


