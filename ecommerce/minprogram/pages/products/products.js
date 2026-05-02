// pages/products/products.js
import { get, post } from '../../utils/request';
import { ensureLoggedIn } from '../../utils/auth';


Page({
  data: {
    allProducts: [],
    products: [],
    categories: [],
    currentCategoryId: 'all',
    currentKeyword: '',
    sortBy: 'default',
    searchValue: '',
    skeletonProducts: [1, 2, 3, 4],
    loading: false,
    addingProductId: null,
    cartMap: {},
    cartCount: 0,
    cartTotal: 0,
    itemQtyMap: {},
    announcementVisible: false,
    announcement: {
      id: null,
      title: '平台公告',
      content: ''
    },
    sortOptions: [
      { label: '默认', value: 'default' },
      { label: '销量', value: 'sales' },
      { label: '价格升序', value: 'price-asc' },
      { label: '价格降序', value: 'price-desc' }
    ]
  },

  onLoad() {
    if (!ensureLoggedIn()) return;
    this.loadPageData();
    this.loadAnnouncement();
  },

  onShow() {
    this.loadProducts().then(() => this.applyFilters());
    const token = wx.getStorageSync('token');
    if (token) {
      this.loadCart();
    }
  },

  onPullDownRefresh() {
    this.loadPageData();
  },

  loadPageData() {
    this.setData({ loading: true });
    Promise.all([this.loadCategories(), this.loadProducts(), this.loadCart()])
      .then(() => this.applyFilters())
      .catch(err => {
        console.error('Load page data error:', err);
      })
      .finally(() => {
        this.setData({ loading: false });
        wx.stopPullDownRefresh();
      });
  },

  loadAnnouncement() {
    if (this.data.announcementVisible) return Promise.resolve();

    return get('/announcement')
      .then(res => {
        const announcement = res || {};
        const hasContent = announcement.is_active && (announcement.content || '').trim() && (announcement.content || '').trim() !== '暂无公告';

        if (!hasContent) return null;

        this.setData({
          announcementVisible: true,
          announcement: {
            id: announcement.id || null,
            title: announcement.title || '平台公告',
            content: announcement.content || ''
          }
        });
        return announcement;
      })
      .catch(err => {
        console.error('Load announcement error:', err);
        return null;
      });
  },

  closeAnnouncement() {
    this.setData({
      announcementVisible: false,
      announcement: {
        id: null,
        title: '平台公告',
        content: ''
      }
    });
  },

  loadCategories() {
    return get('/categories')
      .then(res => {
        const merchantCategories = Array.isArray(res) ? res : (res.data || []);
        const categories = [
          { key: 'all', name: '全部' },
          { key: 'hot', name: '热销' },
          { key: 'promo', name: '促销' },
          ...merchantCategories.map(item => ({
            ...item,
            key: `cat-${item.id}`,
            category_id: item.id
          }))
        ];
        this.setData({ categories });
        return categories;
      })
      .catch(err => {
        console.error('Load categories error:', err);
        const fallbackCategories = [
          { key: 'all', name: '全部' },
          { key: 'hot', name: '热销' },
          { key: 'promo', name: '促销' }
        ];
        this.setData({ categories: fallbackCategories });
        return fallbackCategories;
      });
  },

  loadProducts() {
    return get('/products?page=1&page_size=100')
      .then(res => {
        const products = (Array.isArray(res) ? res : (res.data || [])).map(item => {
          const stock = Number(item.stock || 0);
          return {
            ...item,
            stock,
            isSoldOut: stock <= 0,
            description: item.description || '精选好物，品质推荐'
          };
        });

        this.setData({ allProducts: products });
        return products;
      })
      .catch(err => {
        console.error('Load products error:', err);
        this.setData({ allProducts: [], products: [] });
        return [];
      });
  },

  loadCart() {
    return get('/cart')
      .then(res => {
        const cartItems = Array.isArray(res) ? res : (res.data || []);
        const cartMap = {};
        let cartCount = 0;
        let cartTotal = 0;

        cartItems.forEach(item => {
          cartMap[item.product_id] = item;
          cartCount += item.quantity || 0;
          cartTotal += (item.price || 0) * (item.quantity || 0);
        });

        this.setData({ cartMap, cartCount, cartTotal });
        return cartItems;
      })
      .catch(err => {
        console.error('Load cart error:', err);
        this.setData({ cartMap: {}, cartCount: 0, cartTotal: 0 });
        return [];
      });
  },

  applyFilters() {
    let list = [...this.data.allProducts];
    const currentCategoryId = this.data.currentCategoryId;

    if (currentCategoryId === 'hot') {
      list.sort((a, b) => (b.sales || 0) - (a.sales || 0));
    } else if (currentCategoryId === 'promo') {
      list = list.filter(item => {
        const hasPromoFlag = item.is_promo || item.promo || item.promotion;
        const hasDiscount = typeof item.original_price === 'number' && typeof item.price === 'number' && item.original_price > item.price;
        return hasPromoFlag || hasDiscount;
      });
    } else if (typeof currentCategoryId === 'string' && currentCategoryId.indexOf('cat-') === 0) {
      const categoryId = Number(currentCategoryId.replace('cat-', ''));
      list = list.filter(item => Number(item.category_id) === categoryId);
    }

    if (this.data.currentKeyword) {
      const keyword = this.data.currentKeyword.toLowerCase();
      list = list.filter(item => {
        const name = (item.name || '').toLowerCase();
        const desc = (item.description || '').toLowerCase();
        return name.includes(keyword) || desc.includes(keyword);
      });
    }

    switch (this.data.sortBy) {
      case 'sales':
        list.sort((a, b) => (b.sales || 0) - (a.sales || 0));
        break;
      case 'price-asc':
        list.sort((a, b) => (a.price || 0) - (b.price || 0));
        break;
      case 'price-desc':
        list.sort((a, b) => (b.price || 0) - (a.price || 0));
        break;
      default:
        break;
    }

    this.setData({ products: list });
  },

  handleSearchInput(e) {
    const searchValue = e.detail.value;
    this.setData({ searchValue });
    if (!searchValue.trim()) {
      this.setData({ currentKeyword: '' }, () => this.applyFilters());
    }
  },

  handleSearch() {
    this.setData({ currentKeyword: (this.data.searchValue || '').trim() }, () => {
      this.applyFilters();
    });
  },

  clearSearch() {
    this.setData({ searchValue: '', currentKeyword: '' }, () => {
      this.applyFilters();
    });
  },

  changeSort(e) {
    const sortBy = e.currentTarget.dataset.sort;
    if (!sortBy || sortBy === this.data.sortBy) return;
    this.setData({ sortBy }, () => this.applyFilters());
  },

  selectCategory(e) {
    const categoryId = e.currentTarget.dataset.id || 'all';
    this.setData({ currentCategoryId: categoryId }, () => this.applyFilters());
  },

  // 数量选择器
  handleDecreaseQty(e) {
    const productId = parseInt(e.currentTarget.dataset.productId, 10);
    const map = { ...this.data.itemQtyMap };
    const current = map[productId] || 1;
    if (current > 1) {
      map[productId] = current - 1;
      this.setData({ itemQtyMap: map });
    }
  },

  handleIncreaseQty(e) {
    const productId = parseInt(e.currentTarget.dataset.productId, 10);
    const product = this.data.allProducts.find(p => p.id === productId);
    const maxStock = product ? product.stock : 99;
    const map = { ...this.data.itemQtyMap };
    const current = map[productId] || 1;
    if (current < maxStock) {
      map[productId] = current + 1;
      this.setData({ itemQtyMap: map });
    } else {
      wx.showToast({ title: '已达到库存上限', icon: 'none' });
    }
  },

  handleAddToCart(e) {
    const productId = parseInt(e.currentTarget.dataset.productId, 10);
    if (this.data.addingProductId) return;

    const product = this.data.allProducts.find(item => item.id === productId);
    if (!product) return;

    if (Number(product.stock || 0) <= 0) {
      wx.showToast({ title: '商品已售罄', icon: 'none' });
      return;
    }

    const quantity = this.data.itemQtyMap[productId] || 1;

    this.setData({ addingProductId: productId });
    post('/cart/add', {
      product_id: product.id,
      quantity: quantity
    })
      .then(() => {
        wx.showToast({ title: `已添加 ${quantity} 件到购物车`, icon: 'success', duration: 1000 });
        this.loadCart();
      })
      .catch(err => {
        console.error('Add to cart error:', err);
        wx.showToast({ title: err.message || '添加失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ addingProductId: null });
      });
  },

  handleCheckout() {
    if (this.data.cartCount <= 0) {
      wx.showToast({ title: '购物车是空的', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: '/pages/checkout/checkout' });
  },

  goToCart() {
    wx.switchTab({ url: '/pages/cart/cart' });
  },

  goToDetail(e) {
    const productId = parseInt(e.currentTarget.dataset.productId, 10);
    if (!productId) return;
    wx.navigateTo({
      url: `/pages/product-detail/product-detail?productId=${productId}`
    });
  }
});