import { initHTMXutils } from 'js/utils/htmx'
import { startAlpine } from "js/utils/alpine"
import { initTablePagination } from './utils/table'

startAlpine({
    components: [
    ],
    stores: [
    ]
})

// Add the event listeners for the pagination in the mentorship requests table
initTablePagination("mentorship_req_table")

// Init events listeners for RPC communication beteween the server and the browser
initHTMXutils()

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
// For seeing the details of a student in the
// mentorship request table
window.getStudentInfo = getStudentInfo

