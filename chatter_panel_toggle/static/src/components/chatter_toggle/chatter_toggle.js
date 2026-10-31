/** @odoo-module **/
/* Copyright 2026 Kauko Sirén
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { Chatter } from "@mail/chatter/web_portal_project/chatter";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(Chatter.prototype, {
    setup() {
        super.setup();

        if (this.state) {
            this.state.isChatterVisible = this._getInitialVisibilityState();
        }

        onMounted(() => {
            this._applyChatterVisibility();
        });
    },

    get isChatterVisible() {
        if (this.state && typeof this.state.isChatterVisible === "boolean") {
            return this.state.isChatterVisible;
        }
        return this._getInitialVisibilityState();
    },

    get toggleButtonTitle() {
        return this.isChatterVisible ? _t("Hide Chatter") : _t("Show Chatter");
    },

    get toggleButtonLabel() {
        return this.isChatterVisible ? _t("Hide") : _t("Chatter");
    },

    _getInitialVisibilityState() {
        try {
            const saved = localStorage.getItem("odoo_chatter_visible");
            return saved !== null ? saved === "true" : true;
        } catch {
            return true;
        }
    },

    toggleChatterVisibility() {
        const nextState = !this.isChatterVisible;
        if (this.state) {
            this.state.isChatterVisible = nextState;
        }
        try {
            localStorage.setItem("odoo_chatter_visible", nextState.toString());
        } catch {
            /* ignore */
        }
        this._applyChatterVisibility();
    },

    _applyChatterVisibility() {
        const isVisible = this.isChatterVisible;
        const chatterEl =
            document.querySelector(".o-mail-Form-chatter") ||
            (this.rootRef && this.rootRef.el && this.rootRef.el.closest(".o-mail-Form-chatter")) ||
            document.querySelector(".o_chatter");
        const container =
            document.querySelector(".o_form_view_container") ||
            document.querySelector(".o_content");
        const sheetBg = document.querySelector(".o_form_sheet_bg");

        if (chatterEl) {
            if (isVisible) {
                chatterEl.classList.remove("o-chatter-hidden");
            } else {
                chatterEl.classList.add("o-chatter-hidden");
            }
        }
        if (document.body) {
            if (isVisible) {
                document.body.classList.remove("o-chatter-fullscreen");
            } else {
                document.body.classList.add("o-chatter-fullscreen");
            }
        }
        if (container) {
            if (isVisible) {
                container.classList.remove("o-chatter-fullscreen");
            } else {
                container.classList.add("o-chatter-fullscreen");
            }
        }
        if (sheetBg) {
            if (isVisible) {
                sheetBg.classList.remove("o-chatter-fullscreen");
            } else {
                sheetBg.classList.add("o-chatter-fullscreen");
            }
        }
    },
});
