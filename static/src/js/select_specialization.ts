import Alpine from "alpinejs"

import { myAlpineComponent, startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"

// Component definition
const select_spec = (urlCarrer: string) => ({
    specializations: [],
    search_key: "",
    specialization_selected: Alpine.$persist("").as("specialization"),
    profile: Alpine.$persist("").as("profile"),
    no_tengo: "No tengo especialización",
    errorCarreer: false,
    errorProfile: false,
    urlCarreer: urlCarrer, // The carrer from the url path
    carreer: Alpine.$persist('').as('carreer'),
    // The carrer that is in the url path
    init(){
        // Grab specializations names that came from the server
        this.specializations = JSON.parse(document.getElementById('specializations').textContent);
        // Add and special specializations for people that don't have one
        this.specializations.push(
            {name:this.no_tengo}
        )
        this.errorCarreer = this.carreer != urlCarrer
        this.errorProfile = this.profile == "mentor"
    },
    get next_url(){
        if (this.specialization_selected === this.no_tengo){
            return "/register/select_temas"
        }
        return "/register/complete_profile"
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
const selectSpec: myAlpineComponent = {
    name: "select_spec",
    component: select_spec,
}
// Register component
startAlpine({
    components: [
        selectSpec
    ],
    stores: [
        profileStore
    ]
})
