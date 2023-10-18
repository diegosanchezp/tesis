import Alpine from "alpinejs"

// Global store for instance comunication
Alpine.store('profile', {
    profile: "",
    url: "",
    change(prfl: string){
        this.profile = prfl
    },
    set_url(url: string){
        this.url = url
    }
})

// Component definition
const profile_selector = (_profile: string, selected=false) => ({
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


// Register component
Alpine.data('profile_selector', profile_selector)

Alpine.start()

export { profile_selector }
