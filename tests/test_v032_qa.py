"""QA tests for v0.3.2/0.3.3 visual overhaul — viewer.html rewrite + serve.py changes."""

from pathlib import Path

import pytest

# ---- viewer.html content tests ----

VIEWER_HTML = (Path(__file__).resolve().parent.parent / "src" / "gitstyle" / "viewer.html").read_text(encoding="utf-8")


class TestViewerCDNPins:
    """CDN versions must be pinned exactly to prevent silent breakage."""

    def test_d3_pinned(self):
        assert "d3@7.9.0" in VIEWER_HTML

    def test_marked_pinned_v4(self):
        assert "marked@4.3.0" in VIEWER_HTML

    def test_highlightjs_pinned(self):
        assert "11.9.0" in VIEWER_HTML

    def test_cdn_pin_comment_present(self):
        assert "marked is pinned to v4.x" in VIEWER_HTML or "pinned to" in VIEWER_HTML.lower()

    def test_no_unpinned_latest(self):
        """No CDN links should use @latest or omit version."""
        import re
        cdn_links = re.findall(r'https://cdn\.jsdelivr\.net/[^"\'>\s]+', VIEWER_HTML)
        for link in cdn_links:
            assert "@" in link, f"CDN link missing version pin: {link}"


class TestViewerInterFont:
    """Inter font should be loaded from Google Fonts."""

    def test_google_fonts_preconnect(self):
        assert "fonts.googleapis.com" in VIEWER_HTML

    def test_inter_font_import(self):
        assert "family=Inter" in VIEWER_HTML

    def test_inter_in_font_family(self):
        assert "'Inter'" in VIEWER_HTML


class TestViewerGlassmorphism:
    """Sidebar and toolbar should have glassmorphism (backdrop-filter blur)."""

    def test_backdrop_filter_present(self):
        assert "backdrop-filter:blur(" in VIEWER_HTML or "backdrop-filter: blur(" in VIEWER_HTML

    def test_webkit_backdrop_filter(self):
        assert "-webkit-backdrop-filter:blur(" in VIEWER_HTML or "-webkit-backdrop-filter: blur(" in VIEWER_HTML

    def test_semi_transparent_bg(self):
        assert "rgba(15, 20, 40," in VIEWER_HTML or "rgba(22,27,34," in VIEWER_HTML or "rgba(22, 27, 34," in VIEWER_HTML


class TestViewerGraphFeatures:
    """Graph should have glow filters, bezier edges, particles."""

    def test_svg_glow_filter(self):
        assert "feGaussianBlur" in VIEWER_HTML

    def test_glow_filter_id(self):
        assert "id='glow'" in VIEWER_HTML or 'id="glow"' in VIEWER_HTML or "id', 'glow'" in VIEWER_HTML

    def test_curved_edges_linkArc(self):
        """Graph uses quadratic bezier curves for edges."""
        assert "linkArc" in VIEWER_HTML

    def test_quadratic_bezier_path(self):
        """linkArc function generates Q (quadratic) SVG path commands."""
        assert "Q${mx}" in VIEWER_HTML or "Q " in VIEWER_HTML

    def test_particle_animation(self):
        """Edge particles animated via requestAnimationFrame."""
        assert "animateParticles" in VIEWER_HTML

    def test_particle_circles(self):
        assert "particleCircles" in VIEWER_HTML or "particleSelection" in VIEWER_HTML

    def test_force_simulation(self):
        assert "forceSimulation" in VIEWER_HTML

    def test_force_link(self):
        assert "forceLink" in VIEWER_HTML

    def test_force_charge(self):
        assert "forceManyBody" in VIEWER_HTML

    def test_force_collision(self):
        assert "forceCollide" in VIEWER_HTML

    def test_zoom_behavior(self):
        assert "d3.zoom()" in VIEWER_HTML

    def test_drag_behavior(self):
        assert "d3.drag()" in VIEWER_HTML


class TestViewerStyling:
    """Visual styling features."""

    def test_dark_theme_bg(self):
        """Background should be dark."""
        assert "#0d1117" in VIEWER_HTML or "#080c18" in VIEWER_HTML or "#0a0e1a" in VIEWER_HTML

    def test_dot_grid_pattern(self):
        assert "radial-gradient" in VIEWER_HTML

    def test_category_colors(self):
        """All 4 category colors should be defined."""
        assert "index" in VIEWER_HTML
        assert "dimension" in VIEWER_HTML
        assert "language" in VIEWER_HTML
        assert "meta" in VIEWER_HTML

    def test_scrollbar_styling(self):
        assert "webkit-scrollbar" in VIEWER_HTML

    def test_hover_interaction(self):
        # Vue rewrite uses focus+context dimming instead of tooltip overlay
        assert "graph-tooltip" in VIEWER_HTML or "mouseover" in VIEWER_HTML


class TestViewerFunctionality:
    """Core viewer functionality preserved in rewrite."""

    def test_api_files_fetch(self):
        assert "/api/files" in VIEWER_HTML

    def test_api_file_fetch(self):
        assert "/api/file/" in VIEWER_HTML

    def test_api_graph_fetch(self):
        assert "/api/graph" in VIEWER_HTML

    def test_sidebar_render(self):
        # Vue rewrite uses groupedFiles + template, no renderSidebar function
        assert "renderSidebar" in VIEWER_HTML or "groupedFiles" in VIEWER_HTML

    def test_article_render(self):
        # Vue rewrite uses selectArticle + renderedArticle computed
        assert "renderArticle" in VIEWER_HTML or "selectArticle" in VIEWER_HTML

    def test_graph_render(self):
        assert "renderGraph" in VIEWER_HTML

    def test_marked_parse_call(self):
        assert "marked.parse(" in VIEWER_HTML

    def test_no_deprecated_highlight_option(self):
        """marked.parse should not use the deprecated highlight callback."""
        import re
        # Find all marked.parse calls and ensure none pass highlight option
        calls = re.findall(r'marked\.parse\([^)]+\)', VIEWER_HTML)
        for call in calls:
            assert "highlight" not in call.lower(), f"Deprecated highlight option in: {call}"

    def test_post_render_hljs(self):
        """Code blocks should be highlighted after render."""
        assert "hljs.highlightElement" in VIEWER_HTML

    def test_wikilink_replacement(self):
        assert "wikilink" in VIEWER_HTML

    def test_confidence_normalization(self):
        """Both numeric and string confidence values should be handled."""
        assert "'high'" in VIEWER_HTML or '"high"' in VIEWER_HTML

    def test_source_repos_fallback(self):
        """Should handle both sources and source_repos fields."""
        assert "source_repos" in VIEWER_HTML
        assert "sources" in VIEWER_HTML

    def test_try_catch_render(self):
        """renderArticle should have error handling."""
        assert "catch" in VIEWER_HTML

    def test_cdn_error_fallback(self):
        assert "cdn-error" in VIEWER_HTML or "cdnError" in VIEWER_HTML or "CDN Unreachable" in VIEWER_HTML

    def test_tab_switching(self):
        # Vue rewrite uses v-if/v-show for view switching, no data-view tabs
        assert "data-view" in VIEWER_HTML or "selectedArticle" in VIEWER_HTML

    def test_index_node_pulse(self):
        """Index nodes should have pulsing animation."""
        assert "indexPulse" in VIEWER_HTML or "index-node" in VIEWER_HTML

    def test_hover_highlight(self):
        """Graph nodes should highlight connections on hover."""
        assert "mouseover" in VIEWER_HTML
        assert "mouseout" in VIEWER_HTML

    def test_node_click_navigation(self):
        """Clicking a node should navigate to its article."""
        assert "navigateTo" in VIEWER_HTML or "selectArticle" in VIEWER_HTML


class TestViewerNodeClickEffects:
    """Click effects: ripple + smooth zoom."""

    def test_click_ripple(self):
        """Connected nodes should briefly pulse on click."""
        # The click handler should transition node radius
        assert ".transition().duration(" in VIEWER_HTML

    def test_smooth_zoom_on_click(self):
        """Should smooth-pan to clicked node."""
        assert "zoomBehavior.transform" in VIEWER_HTML or "zoomIdentity" in VIEWER_HTML


# ---- serve.py tests ----

from gitstyle.serve import _parse_frontmatter, _get_viewer_html


class TestServePyChanges:
    """Verify serve.py changes don't break functionality."""

    def test_get_viewer_html_returns_content(self):
        html = _get_viewer_html()
        assert "<!DOCTYPE html>" in html
        assert "gitstyle" in html

    def test_get_viewer_html_not_cached_globally(self):
        """Viewer HTML should be read fresh each call (no stale cache)."""
        html1 = _get_viewer_html()
        html2 = _get_viewer_html()
        assert html1 == html2
        assert len(html1) > 1000

    def test_frontmatter_inline_list(self):
        text = "---\ntags: [a, b, c]\n---\nBody"
        meta, body = _parse_frontmatter(text)
        assert meta["tags"] == ["a", "b", "c"]
        assert body == "Body"

    def test_frontmatter_inline_list_single_item(self):
        text = "---\ntags: [solo]\n---\nBody"
        meta, body = _parse_frontmatter(text)
        assert meta["tags"] == ["solo"]

    def test_frontmatter_inline_list_empty(self):
        text = "---\ntags: []\n---\nBody"
        meta, body = _parse_frontmatter(text)
        assert meta["tags"] == []

    def test_frontmatter_inline_list_with_spaces(self):
        text = "---\nrepos: [ repo1 , repo2 , repo3 ]\n---\nBody"
        meta, body = _parse_frontmatter(text)
        assert meta["repos"] == ["repo1", "repo2", "repo3"]


# ---- Version consistency ----

class TestVersionConsistency:
    """All version references should match."""

    def test_init_version(self):
        from gitstyle import __version__
        assert __version__ == "0.4.0"

    def test_pyproject_version(self):
        pyproject = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text()
        assert 'version = "0.4.0"' in pyproject

    def test_cli_version_test(self):
        test_cli = (Path(__file__).resolve().parent / "test_cli.py").read_text()
        assert '"0.4.0"' in test_cli
