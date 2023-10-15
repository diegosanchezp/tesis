import Alpine from "alpinejs"

// Global store for instance comunication
Alpine.store('profile', {
    profile: "",
    change(prfl: string){
        this.profile = prfl
    }
})

// Component definition
const profile_selector = (_profile: string, selected=false) => ({
    profile: _profile,
    init(){
        if (selected) Alpine.store("profile").change(this.profile)
    },
    /* Computed property to know if the the current component is selected */
    get selected() {
        return Alpine.store("profile").profile == this.profile
    },
    /* onclic event handler, sets the store profile */
    set_current() {
        Alpine.store("profile").change(this.profile)
        console.log(Alpine.store("profile").profile)
    }
})


// Register component
Alpine.data('profile_selector', profile_selector)

Alpine.start()

export { profile_selector }
