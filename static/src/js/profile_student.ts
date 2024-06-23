import { startAlpine } from 'js/utils/alpine'
import { setupProfile } from 'js/utils/profile'
import { openModal } from 'js/utils/modal'
import htmx from 'htmx.org';

const select_spec = () => ({

    specializations: [],
    search_key: "",
    specialization_selected: "",

    init(){
        // Grab specializations names that came from the server
        this.specializations = JSON.parse(document.getElementById('specializations').textContent);
    },

    /** getter for filtering specializations names */
    get filteredSpecialization() {
        let filtSpecializationGroup = []
        filtSpecializationGroup = this.specializations.filter(
            specialization => {
                if (this.search_key != ""){
                    // Perform case insensitive search
                    const regex = new RegExp(this.search_key, "i")
                    return specialization.name.match(regex)
                }
                return specialization
            }
        )
        return filtSpecializationGroup
    },
})
startAlpine({
    stores: [],
    components: [{
        component: select_spec,
        name: "select_spec",
    }],
})

setupProfile()

async function getSpecModal(careerId: string){

    const modalTargetId = "#modal-change-specialization-container"
    await htmx.ajax(
        "GET", `?action=get_specialization_modal&career_id=${careerId}`, {
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

interface OpenSpecModalEvent extends CustomEvent {
    detail: {
        careerId: string
    }
}

async function openSpecModalRPC(evt: OpenSpecModalEvent){
    const { careerId } = evt.detail
    getSpecModal(careerId)

}

document.body.addEventListener("openSpecModal", openSpecModalRPC)

window.getSpecModal = getSpecModal
