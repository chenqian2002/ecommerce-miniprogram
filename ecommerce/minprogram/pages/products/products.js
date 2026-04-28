// pages/products/products.js
import { get, post } from '../../utils/request';

Page({
  data: {
    allProducts: [],
    products: [],
    categories: [],
    currentCategoryId: 0,
    currentKeyword: '',
    sortBy: 'default',
    searchValue: '',
    loading: false,
    cartMap: {},
    cartCount: 0,
    cartTotal: 0,
    sortOptions: [
      { label: '默认', value: 'default' },
      { label: '销量', value: 'sales' },
      { label: '价格升序', value: 'price-asc' },
      { label: '价格降序', value: 'price-desc' }
    ]
  },

  onLoad() {
    this.loadPageData();
  },

    onShow() {
    this.loadCart();
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

  loadCategories() {
    const fixedCategories = [
      { id: 0, name: '全部' },
      { id: 1, name: '热销' },
      { id: 2, name: '促销' }
    ];

    this.setData({ categories: fixedCategories });
    return Promise.resolve(fixedCategories);
  },

  loadProducts() {
    return get('/products?page=1&page_size=100')
      .then(res => {
        const products = (Array.isArray(res) ? res : (res.data || [])).map(item => ({
          ...item,
          description: item.description || '精选好物，品质推荐'
        }));
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

    if (this.data.currentCategoryId) {
      list = list.filter(item => item.category_id === this.data.currentCategoryId);
    }

    if (this.data.currentCategoryId === 1) {
      list.sort((a, b) => (b.sales || 0) - (a.sales || 0));
    } else if (this.data.currentCategoryId === 2) {
      list = list.filter(item => {
        const hasPromoFlag = item.is_promo || item.promo || item.promotion;
        const hasDiscount = typeof item.original_price === 'number' && typeof item.price === 'number' && item.original_price > item.price;
        return hasPromoFlag || hasDiscount;
      });
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
    const categoryId = parseInt(e.currentTarget.dataset.id, 10);
    if (Number.isNaN(categoryId)) return;
    this.setData({ currentCategoryId: categoryId }, () => this.applyFilters());
  },

  handleAddToCart(e) {
    const productId = parseInt(e.currentTarget.dataset.productId, 10);
    const product = this.data.allProducts.find(item => item.id === productId);
    if (!product) return;

    post('/cart/add', {
      product_id: product.id,
      quantity: 1
    })
      .then(() => {
        wx.showToast({ title: '已添加到购物车', icon: 'success', duration: 1000 });
        this.loadCart();
      })
      .catch(err => {
        console.error('Add to cart error:', err);
        wx.showToast({ title: '添加失败', icon: 'none' });
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






