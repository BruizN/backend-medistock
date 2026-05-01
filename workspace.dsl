workspace "Medistock" "Plataforma de comercio electrónico unificada para insumos médicos." {

    model {
        institucion = person "Institución (Clínica)" "Compra insumos médicos al por mayor."
        paciente = person "Paciente" "Compra insumos médicos (B2C)."
        
        medistockSystem = softwareSystem "Medistock E-Commerce" "Plataforma centralizada para venta y distribución de insumos." {
            
            apiApp = container "API RESTful (FastAPI)" "Provee servicios de catálogo, inventario y órdenes" "Python/FastAPI"
            database = container "Base de Datos" "Almacena información de productos, inventario, usuarios y órdenes" "PostgreSQL"
            storageVolume = container "Volumen de Datos" "Persistencia física de la base de datos" "Docker Volume (pg_data)"
            
            apiApp -> database "Lee de y escribe en" "SQL/AsyncPG"
            database -> storageVolume "Almacena datos en" "I/O"
        }

        erpSystem = softwareSystem "Sistemas ERP (Clínicas)" "Sistema externo que consume la API para abastecimiento automatizado."
        
        paymentGateway = softwareSystem "Pasarela de Pagos" "Procesa pagos (Webpay/MercadoPago)."
        logisticsAPI = softwareSystem "API de Logística" "Genera tracking de despachos (Shippo/Mock)."
        
        institucion -> medistockSystem "Realiza pedidos"
        paciente -> medistockSystem "Realiza compras"
        
        erpSystem -> apiApp "Consume catálogo y stock" "REST/HTTPS"
        
        apiApp -> paymentGateway "Inicia pagos" "REST/HTTPS"
        apiApp -> logisticsAPI "Solicita tracking" "REST/HTTPS"
    }

    views {
        systemContext medistockSystem "SystemContext" {
            include *
            autoLayout
        }

        container medistockSystem "Containers" {
            include *
            autoLayout
        }

        theme default
    }
}
