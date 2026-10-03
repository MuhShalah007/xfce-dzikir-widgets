-- Click-through: make conky window pass all mouse input to windows below
-- Uses Xshape extension to set an empty input region

function conky_clickthrough()
    if conky_window == nil then return end
    local cs = cairo_xlib_surface_create(
        conky_window.display,
        conky_window.drawable,
        conky_window.visual,
        conky_window.width,
        conky_window.height
    )
    local cr = cairo_create(cs)
    cairo_destroy(cr)
    cairo_surface_destroy(cs)
end
