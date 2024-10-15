import htmx from 'htmx.org';
import { openModal } from 'js/utils/modal'
import { initTablePagination } from 'js/utils/table'
import { initHTMXutils } from './utils/htmx';

async function getJobApplicationModal(studentId: string, jobId: string){
    const modalTargetId = "#modal-job-application-detail"
    await htmx.ajax(
        "GET", `?action=get_job_application_modal&student=${studentId}&job=${jobId}`, {
        swap: "innerHTML",
        target: modalTargetId
    })
    openModal({
        modalTargetId,
        options: {
            backdropClasses: "z-40",
            backdrop: "dynamic",
        }
    })
}

window.getJobApplicationModal = getJobApplicationModal

initTablePagination("joboffer_applications_table")

initHTMXutils()
