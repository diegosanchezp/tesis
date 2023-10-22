import Alpine from "alpinejs"

import { myAlpineComponent, startAlpine} from "js/utils/alpine"
import {profileStore} from "js/alpine_stores"

// Component definition
const profile_selector_def = (_profile: string, selected=false) => ({
    profile: _profile,
    urls: {},
    init(){
        this.urls = JSON.parse(document.getElementById('form_urls').textContent);
        if (selected) {
            Alpine.store("profile").change(this.profile)
            Alpine.store("profile").set_url(this.urls[this.profile])
        }
        console.log(this.urls);
    },
    /* Computed property to know if the the current component is selected */
    get selected() {
        return Alpine.store("profile").profile == this.profile
    },

    /* onclic event handler, sets the store profile */
    set_current() {
        Alpine.store("profile").change(this.profile)
        Alpine.store("profile").set_url(this.urls[this.profile])
        console.log(Alpine.store("profile").profile)
    }
})

const profileSelector: myAlpineComponent = {
    name: "profile_selector",
    component: profile_selector_def,
}

startAlpine({
    components: [
        profileSelector
    ],
    stores: [
        profileStore
    ]
})
