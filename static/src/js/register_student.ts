import Alpine from "alpinejs"

import {carreraSelector} from "js/components/carrera_selector";

// Register component
Alpine.data('carrera_selector', carreraSelector)

Alpine.start()
