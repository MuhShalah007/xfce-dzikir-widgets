-- dzikir_scroll.lua — scroll Arabic text at UTF-8 character level
-- Conky's ${scroll} works at byte level, breaking Arabic ligatures.
-- This Lua script scrolls at character level, preserving UTF-8 integrity.

local text = "﷽  سُبْحَانَ اللهِ وَبِحَمْدِهِ، سُبْحَانَ اللهِ الْعَظِيمِ  ◆  الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ  ◆  اللَّهُ أَكْبَرُ  ◆  لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ  ◆  اللَّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا مُحَمَّدٍ وَعَلَى آلِهِ وَصَحْبِهِ أَجْمَعِينَ  ◆  رَبَّنَا ظَلَمْنَا أَنْفُسَنَا وَإِنْ لَمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ  ◆  أَسْتَغْفِرُ اللَّهَ الْعَظِيمَ الَّذِي لَا إِلَهَ إِلَّا هُوَ الْحَيَّ الْقَيُّومَ وَأَتُوبُ إِلَيْهِ  ◆  لَا إِلَهَ إِلَّا اللَّهُ  ◆  مُحَمَّدٌ رَسُولُ اللَّهِ  ◆  سُبْحَانَ اللَّهِ  ◆  الْحَمْدُ لِلَّهِ  ◆  اللَّهُ أَكْبَرُ  ◆  لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ  ◆  اللَّهُمَّ إِنَّكَ عَفُوٌّ كَرِيمٌ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي  ◆  رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ  ◆  اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا صَلَّيْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ  ◆  اللَّهُمَّ بَارِكْ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا بَارَكْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ  ◆  "

-- Repeat text 3x for seamless scroll
local full_text = text .. text .. text

-- Count UTF-8 characters (not bytes)
local function utf8_len(s)
    local _, n = string.gsub(s, "[\128-\191]", "")
    return #s - n
end

-- Get UTF-8 substring by character index (1-based)
local function utf8_sub(s, start_char, end_char)
    local pos = 1
    local char_idx = 1
    local start_pos = nil
    local end_pos = nil

    while pos <= #s do
        if char_idx == start_char then
            start_pos = pos
        end
        if char_idx == end_char then
            end_pos = pos
        end

        local b = string.byte(s, pos)
        if b < 128 then
            pos = pos + 1
        elseif b < 224 then
            pos = pos + 2
        elseif b < 240 then
            pos = pos + 3
        else
            pos = pos + 4
        end
        char_idx = char_idx + 1
    end

    if start_pos and end_pos then
        return string.sub(s, start_pos, end_pos - 1)
    elseif start_pos then
        return string.sub(s, start_pos)
    else
        return ""
    end
end

local total_chars = utf8_len(full_text)
local scroll_pos = 1
local window_size = 120  -- characters to show at once

function conky_scroll_dzikir(window)
    local w = tonumber(window) or 120
    window_size = w

    -- Get substring at current scroll position
    local end_pos = scroll_pos + window_size - 1
    if end_pos > total_chars then
        end_pos = total_chars
    end

    local result = utf8_sub(full_text, scroll_pos, end_pos)

    -- Advance scroll position
    scroll_pos = scroll_pos + 1
    if scroll_pos > total_chars then
        scroll_pos = 1
    end

    return result
end
